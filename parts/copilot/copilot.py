import logging
import random

logger = logging.getLogger(__name__)

class Copilot:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {"Stop": 0, "Taxi": 0, "Direction": "Right", "Lane": "Right"}
        logger.info("Successfully Added")

    def update(self):
        mode = self.memory.memory["Mode2"]
        if mode == 1:
            self.memory.memory["Direction"] = "Left"
        if mode == 2:
            self.memory.memory["Direction"] = "Forward"
        if mode == 3:
            self.memory.memory["Direction"] = "Right"

    def shut_down(self):
        self.run = False
        logger.info("Stopped")