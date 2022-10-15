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
        self.arduino_data_thread = threading.Thread(target=lambda a: print("a"))
        # If pilot = manuel self.outputs = {"speed": 0, "steering": 0, "throttle": 0}
        self.arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.006, write_timeout=0.006)
        logger.info("Successfully Added")

    def start_thread(self):
        logger.info("Starting Thread")
        buffer = False
        while self.run:
            while (self.arduino.in_waiting > 0):
                buffer = self.arduino.readline().decode('utf-8')
            # print(data)
            # Looking if data is right format
            if buffer and buffer[0] == "t":
                # re.search(r"t\d+.\d+s\d+.\d+v\d+.\d+e", data)
                data_array = re.split(r't|s|v|e', buffer)
                self.Throttle = float(data_array[1])
                self.Steering = float(data_array[2])
                self.Speed = float(data_array[3])

            time.sleep(0.003)

    def update(self):
        self.memory.memory["Speed"] = self.Speed
        if self.memory.memory["Pilot_Mode"] == "Angle":
            self.memory.memory["Throttle"] = self.Throttle
        elif self.memory.memory["Pilot_Mode"] == "Manuel":
            self.memory.memory["Throttle"] = self.Throttle
            self.memory.memory["Steering"] = self.Steering

        # We want to send the data as fast as we can so we are only sending 2 float, that
        # floats encode motor power and drive mode parameters to throttle and steering values
        # If that float is -1 < float < 1 arduino will use that value to drive motors
        # If float is = 10 arduino won't use that values for controlling the motors 
        pilot_mode_string = self.memory.memory["Pilot_Mode"]
        motor_power = self.memory.memory["Motor_Power"]
        if pilot_mode_string == "Manuel":
            throttle = 10
            steering = 10
        elif pilot_mode_string == "Angle":
            throttle = 10
            steering = self.memory.memory["Steering"]
        elif pilot_mode_string == "Full_Auto":
            throttle = self.memory.memory["Throttle"] * motor_power
            steering = self.memory.memory["Steering"]

        # t is for stating start of throttle value s is for steering and e is for end, \r for read ending
        formatted_data = "t" + str(throttle) + "s" + str(steering) + 'e' + '\r'

        try:
            self.arduino.write(formatted_data.encode())
        except Exception as e:
            # print(e)
            pass
        else:
            # print("succes!!!")
            pass

    def shut_down(self):
        self.run = False
        self.arduino.close()
        logger.info("Stopped")
