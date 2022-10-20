from config import config as cfg

import threading
import logging
import serial
import time
import re

logger = logging.getLogger(__name__)


class Arduino:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.run = True
        self.outputs = {"Speed": 0}
        self.Steering = 0
        self.Throttle = 0
        self.Speed = 0
        # If pilot = manuel self.outputs = {"speed": 0, "steering": 0, "throttle": 0}
        self.arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.006, write_timeout=0.006)
        time.sleep(0.04)
        logger.info("Successfully Added")

    def start_thread(self):
        logger.info("Starting Thread")
        buffer = False
        while self.run:
            while (self.arduino.in_waiting > 0):
                try: buffer = self.arduino.readline().decode('utf-8') 
                except Exception as e: pass
            # Looking if data is right format
            if buffer and buffer[0] == "t":
                # re.search(r"t\d+.\d+s\d+.\d+v\d+.\d+e", data) // todo
                data_array = re.split(r't|s|v|e', buffer)
                self.Throttle = int(data_array[1])
                self.Steering = int(data_array[2])
                # data_array[3] sends ticks/sec we convert it to cm/sec
                self.Speed = float(data_array[3]) / cfg["TICKS_PER_CM"]
            time.sleep(0.003)

    def update(self):
        # self.Throttle, self.Steering and self.Speed values comes from arduino
        # We writing or not writing those values to memory acording to driving mode
        pilot_mode_string = self.memory.memory["Pilot_Mode"]
        self.memory.memory["Speed"] = self.Speed
        if pilot_mode_string == "Angle":
            self.memory.memory["Throttle"] = self.Throttle
        elif pilot_mode_string == "Manuel":
            self.memory.memory["Throttle"] = self.Throttle
            self.memory.memory["Steering"] = self.Steering
        # We want to send the data as fast as we can so we are only sending 2 int as string, those
        # strings encode motor power and drive mode parameters to throttle and steering values
        # If char is 900 < char < 2100 arduino will use that value to drive motors
        # If char is = 10000 arduino won't use that values for controlling the motors
        motor_power = self.memory.memory["Motor_Power"]
        if pilot_mode_string == "Manuel":
            throttle = 10000
            steering = 10000
        elif pilot_mode_string == "Angle":
            throttle = 10000
            steering = self.memory.memory["Steering"]
        elif pilot_mode_string == "Full_Auto":
            throttle = self.memory.memory["Throttle"] * motor_power
            steering = self.memory.memory["Steering"]
        # t is for stating start of throttle value s is for steering and e is for end, \r for read ending
        formatted_data = "t" + str(throttle) + "s" + str(steering) + 'e' + '\r'
        try: self.arduino.write(formatted_data.encode())
        except Exception as e: pass # logger.warning(e)
        else: pass # logger.info("Succes !!!")
            
    def shut_down(self):
        self.run = False
        # If we reading from arduino and close the port that
        # will cause error so we waiting to finish reading then close
        time.sleep(0.04)
        self.arduino.close()
        logger.info("Stopped")
