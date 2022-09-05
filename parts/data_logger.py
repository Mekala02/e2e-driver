import json

class Data_Logger:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {}
        self.save_list = {"IMU", "stop", "taxi", "direction", "lane", "steering", "throttle", "speed", "pilot"}
        self.file = open("myfile.json", "w")

    def update(self):
        json.dump(self.memory.memory, self.file)
        self.file.write('\n')
