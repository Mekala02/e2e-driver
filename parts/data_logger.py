from config import config as cfg

import numpy as np
import datetime
import threading
import logging
import time
import json
import cv2
import os

logger = logging.getLogger(__name__)


class Data_Logger:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {"Data_Id": 0, "Timestamp": 0}
        self.index = 0
        self.save_it = {"Data_Id", "Zed_Data_Id", "Timestamp", "Zed_Timestamp", "Steering", "Throttle", "Speed", "Mode1", "Mode2", "IMU_Accel_X", "IMU_Accel_Y", "IMU_Accel_Z", "IMU_Gyro_X", "IMU_Gyro_Y", "IMU_Gyro_Z",
        "Stop", "Taxi", "Direction", "Lane", "Pilot_Mode", "Route_Mode", "Motor_Power", "Record", "Speed_Factor", "Fps"}

        # If user not specified data folder it will named according to date
        if not "Data_Folder" in self.memory.memory:
            new_folder_name = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
            data_folder = os.path.join("data", new_folder_name)  
            memory.memory["Data_Folder"] = data_folder

        self.data_folder = memory.memory["Data_Folder"]
        os.mkdir(self.data_folder)

        with open(os.path.join(self.data_folder, "cfg.json"), "w+") as config_log:
            json.dump(cfg, config_log)
        # If we saving data in svo file don't creating folders
        if cfg["SVO_COMPRESSION_MODE"] is None:
            os.mkdir(os.path.join(self.data_folder, "Color_Image"))
            os.mkdir(os.path.join(self.data_folder, "Depth_Image"))
            os.mkdir(os.path.join(self.data_folder, "Object_Detection"))
        self.file = open(os.path.join(self.data_folder, "memory.json"), "w+")
        self.file.write("[")
        logger.info("Successfully Added")
        logger.info(f"Data_Folder: {self.data_folder}")

    def save_to_file(self, img_format, path, name, data):
        if img_format == "npy":
            np.save(os.path.join(path, name+".npy"), data)
        elif img_format == "npz":
            np.savez_compressed(os.path.join(path, name+".npz"), data)
        elif img_format == "jpg" or img_format == "jpeg" or img_format == "png":
            cv2.imwrite(os.path.join(path, name+"." + img_format), data)
        else:
            logger.warning("Unknown Image Format")
    
    def save_json(self, opened_file, data):
        json.dump(data, opened_file)
        opened_file.write(',')
        opened_file.write('\n')

    def update(self):
        self.memory.memory["Data_Id"] = self.index
        self.memory.memory["Timestamp"] = int(time.time_ns())
        if self.memory.memory["Record"]:
            data = {key:self.memory.memory[key] for key in self.save_it}
            self.save_json(self.file, data)
            if cfg["SVO_COMPRESSION_MODE"] is None:
                threading.Thread(target=self.save_to_file,
                    args=([cfg["COLOR_IMAGE_FORMAT"], os.path.join(self.data_folder, "Color_Image"), str(self.index), self.memory.big_memory["RGB_Image"]]),
                    daemon=True,
                    name="Rgb_Image").start()
                threading.Thread(target=self.save_to_file,
                    args=([cfg["DEPTH_IMAGE_FORMAT"], os.path.join(self.data_folder, "Depth_Image"), str(self.index), self.memory.big_memory["Depth_Array"]]),
                    daemon=True,
                    name="Depth_Array").start()
            self.index += 1
    
    def shut_down(self):
        self.run = False
        # Move the pointer (similar to a cursor in a text editor) to the end of the file
        self.file.seek(0, os.SEEK_END)
        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = self.file.tell() - 1
        # Read each character in the file one at a time from the penultimate
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and self.file.read(1) != ",":
            pos -= 1
            self.file.seek(pos, os.SEEK_SET)
        # So long as we're not at the start of the file, delete all the characters ahead
        # of this position
        if pos > 0:
            self.file.seek(pos, os.SEEK_SET)
            self.file.truncate()
        self.file.write(']')
        self.file.close()
        logger.info("Stopped")