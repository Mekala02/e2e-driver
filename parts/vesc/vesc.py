from common_functions import PID, Limiter, pwm2float, float2pwm

import pyvesc
import inputs
import threading
import logging
import serial
import io
import time
import re

logger = logging.getLogger(__name__)

class Vesc:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.thread_hz = memory.cfg["DRIVE_LOOP_HZ"]
        self.run = True
        self.outputs = {}
        self.steering = 0
        self.throttle = 0

        self.act_value_type = memory.cfg["ACT_VALUE_TYPE"]
        self.steering_limiter = Limiter(min_=memory.cfg["STEERING_MIN"], max_=memory.cfg["STEERING_MAX"])
        self.throttle_limiter = Limiter(min_=memory.cfg["THROTTLE_MIN"], max_=memory.cfg["THROTTLE_MAX"])
        self.steering_offset = memory.cfg["STEERING_OFFSET"]

        self.vesc = pyvesc.VESC(serial_port="/dev/ttyACM0")

        time.sleep(0.04)
        logger.info("Successfully Added")
        

    def update(self):
        steering = self.steering_limiter(-self.memory.memory["Steering"])
        self.vesc.set_servo(steering+self.steering_offset)
        throttle = self.throttle_limiter(self.memory.memory["Throttle"] * self.memory.memory["Motor_Power"])
        self.vesc.set_duty_cycle(throttle)

    def shut_down(self):
        self.run = False
        time.sleep(0.05)
        logger.info("Stopped")
