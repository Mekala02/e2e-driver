from common_functions import PID, Limiter, pwm2float, float2pwm

import threading
import logging
import serial
import io
import time
import re

logger = logging.getLogger(__name__)


class Arduino:
    def __init__(self, memory):
        self.memory = memory
        self.thread = "Single"
        self.thread_hz = 120
        self.run = True
        self.outputs = {"Steering": 0, "Throttle": 0, "Speed": 0, "Mode1": 0, "Mode2": 0, "Target_Speed": None}
        # Also It can output Act_Value, Record and drive mode acoording to mode button
        self.act_value_type = memory.cfg["ACT_VALUE_TYPE"]
        self.Steering_A = 1500
        self.Act_Value_A = 1500
        self.Speed_A = 0
        self.Mode1 = 0
        self.Mode2 = 0
        self.Steering = 0
        self.Act_Value = 0
        self.Speed = 0
        self.Throttle = 0
        self.arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.006, write_timeout=0.006)
        time.sleep(0.04)
        logger.info("Successfully Added")

    def grab_data(self):
        buffer = False
        try: buffer = self.arduino.read(self.arduino.in_waiting).decode('utf-8') 
        except Exception as e: pass
        # Looking if data is right format
        if buffer and buffer[0] == "s":
            # re.search(r"t\d+.\d+s\d+.\d+v\d+.\d+e", data) // todo
            data_array = re.split(r's|t|m|m|v|e', buffer)
            self.Steering_A = int(data_array[1])
            self.Act_Value_A = int(data_array[2])
            # if 0 --> radio turned off, elif 1 --> mode 1, elif 2 --> mode 2
            self.Mode1 = int(data_array[3])
            self.Mode2 = int(data_array[4])
            self.Speed_A = float(data_array[5])

    def start_thread(self):
        logger.info("Starting Thread")
        while self.run:
            start_time = time.time()
            self.grab_data()
            # Arduino sends data @100hz we limiting the thread speed to @120hz
            sleep_time = 1.0 / self.thread_hz - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        pilot_mode_string = self.memory.memory["Pilot_Mode"]
        self.Act_Value = pwm2float(self.Act_Value_A)
        if pilot_mode_string == "Manuel" or pilot_mode_string == "Angle":
            if self.act_value_type == "Throttle":
                self.Throttle = self.Act_Value
            self.memory.memory["Throttle"] = self.Throttle
            if pilot_mode_string == "Manuel":
                self.Steering = -pwm2float(self.Steering_A)
                self.memory.memory["Steering"] = self.Steering

        self.memory.memory["Mode1"] = self.Mode1
        self.memory.memory["Mode2"] = self.Mode2

    def shut_down(self):
        self.run = False
        # If we reading from arduino and close the port that
        # will cause error so we waiting to finish reading then close
        time.sleep(0.05)
        self.arduino.close()
        logger.info("Stopped")
