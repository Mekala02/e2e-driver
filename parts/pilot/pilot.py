import math
import time
import logging

logger = logging.getLogger(__name__)

class Pilot:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.run = False
        self.outputs = {"Steering": 0, "Throttle": 0}

        self.i = 0
        logger.info("Successfully Added")
        
    def update(self):
        # Sin vave for testing web server
        if self.memory.memory["Pilot_Mode"] == "Angle":
            self.memory.memory["Steering"] = int(1500 + math.sin(time.time()) * 600)
        elif self.memory.memory["Pilot_Mode"] == "Full_Auto":
            self.memory.memory["Throttle"] = int(1500 + math.sin(time.time() + 2) * 600)
            self.memory.memory["Steering"] = int(1500 + math.sin(time.time()) * 600)

    def shut_down(self):
        self.run = False
        logger.info("Stopped")
