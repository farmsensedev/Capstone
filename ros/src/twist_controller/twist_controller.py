from yaw_controller import YawController
from lowpass import LowPassFilter
from pid import PID

import rospy

GAS_DENSITY = 2.858
ONE_MPH = 0.44704


class Controller(object):
    def __init__(self, *args, **kwargs):
        self.throttle_control = PID(
                                kp = 3.0,
                                ki = 2.4,
                                kd = 1.0,
                                mn = -1.0,
                                mx = 1.0)

        self.steer_control = PID(
                                kp=1.0,
                                ki=0.0,
                                kd=0.05)

        self.steering_control = YawController(kwargs['wheel_base'], kwargs['steer_ratio'],
                                         kwargs['min_speed'], kwargs['max_lat_accel'],
                                         kwargs['max_steer_angle']
                                         )
                                         
        self.time = None
        self.max_vel = kwargs['max_vel']
        self.accel_limit = kwargs['accel_limit']
        self.decel_limit = kwargs['decel_limit']
        self.TP1_throttle = LowPassFilter(0.5, 0.1)
        self.linear_pid = PID(kp=0.8, ki=0, kd=0.05, mn=self.decel_limit, mx=0.5 * self.accel_limit)

    def control(self, *args, **kwargs):
        linear_velocity = kwargs['target_linear_velocity']
        angular_velocity = kwargs['target_angular_velocity']
        current_velocity = kwargs['current_linear_velocity']

        dbw_state = kwargs['dbw_state']

        if self.time is None or not dbw_state:
            self.time = rospy.get_time()
            return 0.0, 0.0, 0.0
            
        dt = rospy.get_time() - self.time

        steer = self.steering_control.get_steering(linear_velocity, angular_velocity, current_velocity)
        steer = self.steer_control.step(steer, dt)

        linear_velocity_error = linear_velocity - current_velocity

        velocity_correction = self.linear_pid.step(linear_velocity_error, 3.0 #duration_in_seconds
            )

        throttle = velocity_correction

        # we need throttle can be minus, i.e. < 0, when car needs slow down
        if throttle_2 < 0:
            throttle = 0.0
            brake = -throttle * 20
            brake = 100
        else:
            brake = 0.0
        
        self.time = rospy.get_time()
        return throttle, brake, steer
