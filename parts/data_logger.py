import json
import datetime
import os
import time
import numpy as np
import threading

class Data_Logger:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"Img_Id": 0, "Timestamp": 0}

        # self.save_list = {"Img_Id": 0, "Timestamp": 0, "Steering": 0, "Throttle": 0, "Speed": 0, "IMU": 0, "Direction": 0, "Lane": 0, "Stop": 0, "Taxi": 0, "Pilot": 0, "Route": 0}
        new_folder_name = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        data_folder = os.path.join("data", new_folder_name)
        os.mkdir(data_folder)
        self.images_folder = os.path.join(data_folder, "images")
        os.mkdir(self.images_folder)
        os.mkdir(os.path.join(self.images_folder, "Depth"))
        os.mkdir(os.path.join(self.images_folder, "RGB"))
        os.mkdir(os.path.join(self.images_folder, "Object_Detection"))

        self.file = open(os.path.join(data_folder, "memory.json"), "w+")
        self.file.write("[")
        self.index = 0

    def save_to_file(self, path, data):
        np.save(path, data)
    
    def save_json(self, opened_file, data):
        json.dump(data, opened_file)
        opened_file.write(',')
        opened_file.write('\n')

    def update(self):
        self.memory.memory["Img_Id"] = self.index
        self.memory.memory["Timestamp"] = int(time.time_ns() * 1e-6)
        if self.memory.memory["Record"]:
            # for key, value in self.memory.memory.items():
            #     if key in self.save_list:
            #         self.save_list[key] = self.memory.memory[key]
            # json.dump(self.save_list, self.file)
            self.save_json(self.file, self.memory.memory)
            for key, value in self.memory.big_memory.items():
                threading.Thread(target=self.save_to_file, args=([os.path.join(self.images_folder, key, f"{self.index}.npy"), value]), daemon=True).start()
                break
            self.index += 1
    
    def shut_down(self):
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