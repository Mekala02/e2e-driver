from config import config as cfg

import threading
import logging
import serial
import time
import re

logger = logging.getLogger(__name__)


class Arduino:
    def __init__(self, memory):
        self.memory = memory
        self.thread = "Single"
        self.run = True
        self.outputs = {"Speed": 0, "Mode_Button": 0}
        # Also It can output Record and drive mode acoording to mode button 
        self.Steering = 0
        self.Throttle = 0
        self.mode_button = 0
        self.Speed = 0
        # If pilot = manuel self.outputs = {"speed": 0, "steering": 0, "throttle": 0}
        self.arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.006, write_timeout=0.006)
        time.sleep(0.04)
        logger.info("Successfully Added")

    def grab_data(self):
        buffer = False
        while (self.arduino.in_waiting > 0):
            try: buffer = self.arduino.readline().decode('utf-8') 
            except Exception as e: pass
        # Looking if data is right format
        if buffer and buffer[0] == "s":
            # re.search(r"t\d+.\d+s\d+.\d+v\d+.\d+e", data) // todo
            data_array = re.split(r's|t|m|v|e', buffer)
            self.Steering = int(data_array[1])
            self.Throttle = int(data_array[2])
            # if 0 --> radio turned off, elif 1 --> mode 1, elif 2 --> mode 2
            self.mode_button = int(data_array[3])
            # data_array[3] sends ticks/sec we convert it to cm/sec
            self.Speed = float(data_array[4]) / cfg["TICKS_PER_CM"]

    def start_thread(self):
        logger.info("Starting Thread")
        while self.run:
            start_time = time.time()
            self.grab_data()
            sleep_time = 1.0 / cfg["CAMERA_FPS"] - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        # self.Throttle, self.Steering and self.Speed values comes from arduino
        # We writing or not writing those values to memory acording to driving mode
        pilot_mode_string = self.memory.memory["Pilot_Mode"]
        if pilot_mode_string == "Angle":
            self.memory.memory["Throttle"] = self.Throttle
        elif pilot_mode_string == "Manuel":
            self.memory.memory["Throttle"] = self.Throttle
            self.memory.memory["Steering"] = self.Steering
        self.memory.memory["Speed"] = self.Speed
        self.memory.memory["Mode_Button"] = self.mode_button
        # We want to send the data as fast as we can so we are only sending 2 int as string, those
        # strings encode motor power and drive mode parameters to throttle and steering values
        # If char is 1000 < char < 2000 arduino will use that value to drive motors
        # If char is = 0 arduino won't use that values for controlling the motors
        motor_power = self.memory.memory["Motor_Power"]
        if pilot_mode_string == "Manuel":
            steering = 0
            throttle = 0
        elif pilot_mode_string == "Angle":
            steering = self.memory.memory["Steering"]
            throttle = 0
        elif pilot_mode_string == "Full_Auto":
            steering = self.memory.memory["Steering"]
            throttle = self.memory.memory["Throttle"] * motor_power
        # s is for stating start of throttle value t is for steering and e is for end, \r for read ending
        formatted_data = "s" + str(steering) + "t" + str(throttle) + 'e' + '\r'
        try: self.arduino.write(formatted_data.encode())
        except Exception as e: pass # logger.warning(e)
        else: pass # logger.info("Succes !!!")
            
    def shut_down(self):
        self.run = False
        # If we reading from arduino and close the port that
        # will cause error so we waiting to finish reading then close
        time.sleep(0.05)
        self.arduino.close()
        logger.info("Stopped")
