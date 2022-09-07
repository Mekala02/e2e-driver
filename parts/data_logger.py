import json
import time
import numpy as np
# import os

class Data_Logger:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"index": 0, "timestamp": 0}
        self.save_list = {"IMU", "stop", "taxi", "direction", "lane", "steering", "throttle", "speed", "pilot"}
        self.file = open(f"data/memory.json", "w")
        self.index = 0

    def save_image(self, path, data):
        np.save(path, data)

    def update(self):
        self.memory.memory["index"] = self.index
        self.memory.memory["timestamp"] = int(time.time_ns() * 1e-6)
        if self.memory.memory["record"]:
            json.dump(self.memory.memory, self.file)
            self.file.write('\n')
            for key, value in self.memory.big_memory.items():
                self.save_image(f"data/images/{key}/{self.index}.npy", value)
            self.index += 1

