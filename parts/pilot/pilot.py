import math
import time
import torch
import logging

logger = logging.getLogger(__name__)


class Pilot:
    def __init__(self, memory):
        self.memory = memory
        self.threaded = False
        self.run = False
        self.outputs = {"Steering": 0, "Throttle": 0}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Torch Device: {self.device}")
        logger.info("Successfully Added")  
        self.i = 0
        
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
