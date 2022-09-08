import json
import time
import numpy as np
import threading

class Data_Logger:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"index": 0, "timestamp": 0}

        self.save_list = {"img_id": 0, "timestamp": 0, "steering": 0, "throttle": 0, "speed": 0, "IMU": 0, "direction": 0, "lane": 0, "stop": 0, "taxi": 0, "pilot": 0, "route": 0}
        self.file = open(f"data/memory.json", "w")
        self.index = 0

    def save_image(self, path, data):
        np.save(path, data)

    def update(self):
        self.memory.memory["index"] = self.index
        self.memory.memory["timestamp"] = int(time.time_ns() * 1e-6)
        if self.memory.memory["record"]:
            for key, value in self.memory.memory.items():
                if key in self.save_list:
                    self.save_list[key] = self.memory.memory[key]
            json.dump(self.save_list, self.file)
            self.file.write('\n')
            for key, value in self.memory.big_memory.items():
                threading.Thread(target=self.save_image, args=([f"data/images/{key}/{self.index}.npy", value])).start()
            self.index += 1