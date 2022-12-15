from common_functions import PID, Limiter, pwm2float, float2pwm
from config import config as cfg

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
        self.outputs = {"Steering": 0, "Throttle": 0, "Speed": 0, "Mode1": 0, "Mode2": 0}
        # Also It can output Record and drive mode acoording to mode button
        self.act_value_type = cfg["ACT_VALUE_TYPE"]
        self.Steering_A = 1500
        self.Act_Value_A = 1500
        self.Speed_A = 0
        self.Mode1 = 0
        self.Mode2 = 0
        self.Steering = 0
        self.Act_Value = 0
        self.Speed = 0
        self.Throttle = 0
        self.ticks_per_unit = cfg["ENCODER_TICKS_PER_UNIT"]
        self.stick_multiplier = cfg["TRANSMITTER_STICK_SPEED_MULTIPLIER"]
        self.steering_limiter = Limiter(min_=pwm2float(cfg["STEERING_MIN_PWM"]), max_=pwm2float(cfg["STEERING_MAX_PWM"]))
        self.throttle_limiter = Limiter(min_=pwm2float(cfg["THROTTLE_MIN_PWM"]), max_=pwm2float(cfg["THROTTLE_MAX_PWM"]))
        if self.act_value_type == "Speed":
            self.pid = PID(Kp=cfg["K_PID"]["Kp"], Ki=cfg["K_PID"]["Ki"], Kd=cfg["K_PID"]["Kd"], I_max=cfg["K_PID"]["I_max"])
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
        '''
        We want to send the data as fast as we can so we are only sending 2 int as string, those
        strings encode motor power and drive mode parameters to throttle and steering values
        If char is between 1000, 2000 arduino will use that value to drive motors
        If char is = 0 arduino won't use that value for controlling the actuator
        '''
        # Speed_A is ticks/sec we converting it to unit/sec
        self.Speed = self.Speed_A / self.ticks_per_unit
        pilot_mode_string = self.memory.memory["Pilot_Mode"]
        if pilot_mode_string == "Manuel" or pilot_mode_string == "Angle":
            if self.act_value_type == "Throttle":
                self.Throttle = self.throttle_limiter(pwm2float(self.Act_Value_A))
                Throttle_Signal = 0
            elif self.act_value_type == "Speed":
                # Act_Value_A is between 0, 1 we multipliying it by Stick_Multiplier
                # for converting to speed
                self.Throttle = self.pid(self.Speed, self.stick_multiplier * pwm2float(self.Act_Value_A))
                self.Throttle = self.throttle_limiter(self.Throttle)
                Throttle_Signal = float2pwm(self.Throttle)
            if pilot_mode_string == "Manuel":
                # Steering value increases when turning to left so we reversing it with -
                self.Steering = self.steering_limiter(-pwm2float(self.Steering_A))
                self.memory.memory["Steering"] = self.stick_multiplier * pwm2float(self.Act_Value_A)
                Steering_Signal = 0
            elif pilot_mode_string == "Angle":
                # Rereversing with -
                Steering_Signal = float2pwm(-self.memory.memory["Steering"])
        elif pilot_mode_string == "Full_Auto":
            if self.act_value_type == "Throttle":
                self.throttle = self.throttle_limiter(self.memory.memory["Act_Value"])
            elif self.act_value_type == "Speed":
                self.throttle = self.throttle_limiter(self.pid(self.speed, self.memory.memory["Act_Value"]))
            Steering_Signal = float2pwm(self.memory.memory["Steering"])
            # Motor power: 0 or 1
            Throttle_Signal = float2pwm(self.throttle * self.memory.memory["Motor_Power"])
        
        self.memory.memory["Throttle"] = self.Throttle
        self.memory.memory["Speed"] = self.Speed
        self.memory.memory["Mode1"] = self.Mode1
        self.memory.memory["Mode2"] = self.Mode2

        # s is for stating start of steering value t is for throttle and e is for end, \r for read ending
        formatted_data = "s" + str(Steering_Signal) + "t" + str(Throttle_Signal) + 'e' + '\r'
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
