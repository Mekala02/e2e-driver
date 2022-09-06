import json
import time

class Data_Logger:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"index": 0, "timestamp": 0}
        self.save_list = {"IMU", "stop", "taxi", "direction", "lane", "steering", "throttle", "speed", "pilot"}
        self.file = open("myfile.json", "w")
        self.index = 0

    def update(self):
        self.memory.memory["index"] = self.index
        self.memory.memory["timestamp"] = time.time_ns() / 1e-6
        # json.dump(self.memory.memory, self.file)
        # self.file.write('\n')
        self.index += 1
