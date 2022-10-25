import logging
import random

logger = logging.getLogger(__name__)

class Copilot:
    def __init__(self, memory):
        self.memory = memory
        self.threaded = False
        self.run = True
        self.outputs = {"Stop": 0, "Taxi": 0, "Direction": "Right", "Lane": "Right"}

        self.directions = ["Left", "Forward", "Right"]
        self.lanes = ["Left", "Right"]
        self.counter = 0
        logger.info("Successfully Added")

    def update(self):
        self.counter += 1
        if self.counter%1000 == 1:
            self.memory.memory["Direction"] = random.choice(self.directions)
            self.memory.memory["Stop"] = random.randint(0, 1)
            self.memory.memory["Taxi"] = random.randint(0, 1)
            self.memory.memory["Lane"] = random.choice(self.lanes)

    def shut_down(self):
        self.run = False
        logger.info("Stopped")