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
        self.memory.memory["Steering"] = math.sin(time.time())
        self.memory.memory["Throttle"] = math.sin(time.time() + 2)

    def shut_down(self):
        self.run = False
        logger.info("Stopped")
