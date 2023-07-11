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
        self.steering_limiter = Limiter(min_=pwm2float(memory.cfg["STEERING_MIN_PWM"]), max_=pwm2float(memory.cfg["STEERING_MAX_PWM"]))
        self.throttle_limiter = Limiter(min_=pwm2float(memory.cfg["THROTTLE_MIN_PWM"]), max_=pwm2float(memory.cfg["THROTTLE_MAX_PWM"]))
        if self.act_value_type == "Speed":
            self.Target_Speed = 0
            self.pid = PID(Kp=memory.cfg["K_PID"]["Kp"], Ki=memory.cfg["K_PID"]["Ki"], Kd=memory.cfg["K_PID"]["Kd"], I_max=memory.cfg["K_PID"]["I_max"])
        
        self.vesc = pyvesc.VESC(serial_port="/dev/ttyACM0")

        time.sleep(0.04)
        logger.info("Successfully Added")
        

    def update(self):
        self.vesc.set_servo(-self.memory.memory["Steering"]+0.53)
        throttle = self.memory.memory["Throttle"] * self.memory.memory["Motor_Power"]
        self.vesc.set_duty_cycle(min(max(throttle, -0.05), 0.05))

    def shut_down(self):
        self.run = False
        time.sleep(0.05)
        logger.info("Stopped")
