import json
import time
import numpy as np
import threading

class Data_Logger:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"Index": 0, "Timestamp": 0}

        self.save_list = {"Img_Id": 0, "Timestamp": 0, "Steering": 0, "Throttle": 0, "Speed": 0, "IMU": 0, "Direction": 0, "Lane": 0, "Stop": 0, "Taxi": 0, "Pilot": 0, "Route": 0}
        self.file = open(f"data/memory.json", "w")
        self.index = 0

    def save_image(self, path, data):
        np.save(path, data)

    def update(self):
        self.memory.memory["Index"] = self.index
        self.memory.memory["Timestamp"] = int(time.time_ns() * 1e-6)
        if self.memory.memory["Record"]:
            for key, value in self.memory.memory.items():
                if key in self.save_list:
                    self.save_list[key] = self.memory.memory[key]
            json.dump(self.save_list, self.file)
            self.file.write('\n')
            for key, value in self.memory.big_memory.items():
                threading.Thread(target=self.save_image, args=([f"data/images/{key}/{self.index}.npy", value]), daemon=True).start()
            self.index += 1