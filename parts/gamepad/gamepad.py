from common_functions import PID, Limiter, pwm2float, float2pwm

from inputs import devices
import threading
import logging
import serial
import io
import time
import re

logger = logging.getLogger(__name__)


class Gamepad:
    def __init__(self, memory):
        self.memory = memory
        self.thread = "Single"
        self.thread_hz = 120
        self.run = True
        self.outputs = {"Steering": 0, "Throttle": 0, "Speed": 0, "Mode1": 0, "Mode2": 0, "Target_Speed": None}
        # Also It can output Act_Value, Record and drive mode acoording to mode button
        self.act_value_type = memory.cfg["ACT_VALUE_TYPE"]
        self.Steering_G = 0
        self.Act_Value_G = 0
        self.Speed_A = 0
        self.Mode1 = 0
        self.Mode2 = 0
        self.Steering = 0
        self.Act_Value = 0
        self.Speed = 0
        self.Throttle = 0
        self.ticks_per_unit = memory.cfg["ENCODER_TICKS_PER_UNIT"]
        self.stick_multiplier = memory.cfg["TRANSMITTER_STICK_SPEED_MULTIPLIER"]
        self.steering_limiter = Limiter(min_=pwm2float(memory.cfg["STEERING_MIN_PWM"]), max_=pwm2float(memory.cfg["STEERING_MAX_PWM"]))
        self.throttle_limiter = Limiter(min_=pwm2float(memory.cfg["THROTTLE_MIN_PWM"]), max_=pwm2float(memory.cfg["THROTTLE_MAX_PWM"]))
        if self.act_value_type == "Speed":
            self.Target_Speed = 0
            self.pid = PID(Kp=memory.cfg["K_PID"]["Kp"], Ki=memory.cfg["K_PID"]["Ki"], Kd=memory.cfg["K_PID"]["Kd"], I_max=memory.cfg["K_PID"]["I_max"])

        time.sleep(0.04)
        logger.info("Successfully Added")


    def grab_data(self):
        events = devices.gamepads[0]._do_iter()
        event = events[-1]
        # for event in events:
        if event.code == "ABS_RX":
            self.Steering_G = event.state/32768
        if event.code == "ABS_Y":
            self.Act_Value_G = -event.state/32768

    def start_thread(self):
        logger.info("Starting Thread")
        while self.run:
            start_time = time.time()
            self.grab_data()
            # print(self.Act_Value_G )
            # Arduino sends data @100hz we limiting the thread speed to @120hz
            sleep_time = 1.0 / self.thread_hz - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        pilot_mode_string = self.memory.memory["Pilot_Mode"]
        self.Act_Value = self.Act_Value_G
        if pilot_mode_string == "Manuel" or pilot_mode_string == "Angle":
            self.Throttle = self.Act_Value
            self.memory.memory["Throttle"] = self.Throttle
            if pilot_mode_string == "Manuel":
                self.Steering = self.Steering_G
                self.memory.memory["Steering"] = self.Steering

        # self.memory.memory["Speed"] = self.Speed
        # self.memory.memory["Mode1"] = self.Mode1
        # self.memory.memory["Mode2"] = self.Mode2

    def shut_down(self):
        self.run = False
        # If we reading from arduino and close the port that
        # will cause error so we waiting to finish reading then close
        time.sleep(0.05)
        logger.info("Stopped")
