import math
import time

class Pilot:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"steering": 0, "throttle": 0}

        self.i = 0

    def update(self):
        # Sin vave for testing web server
        self.memory.memory["steering"] = math.sin(time.time())
        self.memory.memory["throttle"] = math.sin(time.time() + 1)
