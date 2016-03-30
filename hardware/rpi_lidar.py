__author__ = 'StaticVOiDance'


import atexit
from .lidar import Lidar
from .constants import *

import wiringpi2 as wiringpi
pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupPhys()
PWM_PIN = 12
wiringpi.pinMode(PWM_PIN, 2) #pwm mode
wiringpi.pwmWrite(PWM_PIN, 0)


class RPi_Lidar(Lidar):
    def __del__(self):
        self.set_motor_duty(0)

    def connect(self, hw_addr: str):
        self.set_motor_duty(0)
        super(RPi_Lidar, self).connect(hw_addr)

    @staticmethod
    def set_motor_duty(duty_cycle):
        assert 0 <= duty_cycle <= 100
        duty_cycle = int(duty_cycle * 10.24)
        wiringpi.pwmWrite(PWM_PIN, duty_cycle)

    async def set_target_speed(self, rot_per_sec):
        assert V_SCALE_MIN <= rot_per_sec <= V_SCALE_MAX
        duty = int(V_SCALE_MAX*rot_per_sec) + V_SCALE_MIN
        rate = await self.get_current_speed()
        if rot_per_sec > rate:
            count = 1
        else:
            count = -1
        for modifier in range(0, count*100, count):
            self.set_motor_duty(duty+modifier)
            rate = await self.get_current_speed()
            if not round(abs(rate - rot_per_sec), -1):
                return

@atexit.register
def cleanup_gpio():
    RPi_Lidar.set_motor_duty(0)
