import logging

logger = logging.getLogger(__name__)

class DAgger:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {}
        self.overwrite_importance = 1
        self.overwrites = {"Record", "Pilot_Mode"}
        logger.info("Successfully Added")

    def update(self):
        # Not recording and manuel mode
        if self.memory.memory["Mode1"] == 1:
            if not("Record" in self.memory.overwrite and self.overwrite_importance < self.memory.overwrite["Record"]["importance"]):
                self.memory.memory["Record"] = 0
                self.memory.overwrite["Record"] = {"importance": self.overwrite_importance, "value": 0}
            if not ("Pilot_Mode" in self.memory.overwrite and self.overwrite_importance < self.memory.overwrite["Pilot_Mode"]["importance"]):
                self.memory.memory["Pilot_Mode"] = "Manuel"
                self.memory.overwrite["Pilot_Mode"] = {"importance": self.overwrite_importance, "value": "Manuel"}
        # Not recording and self driving in angle mode
        elif self.memory.memory["Mode1"] == 2:
            # If our importance is higher then other overwrite writing the value
            if not("Record" in self.memory.overwrite and self.overwrite_importance < self.memory.overwrite["Record"]["importance"]):
                self.memory.memory["Record"] = 0
                self.memory.overwrite["Record"] = {"importance": self.overwrite_importance, "value": 0}
            if not("Pilot_Mode" in self.memory.overwrite and self.overwrite_importance < self.memory.overwrite["Pilot_Mode"]["importance"]):
                self.memory.memory["Pilot_Mode"] = "Angle"
                self.memory.overwrite["Pilot_Mode"] = {"importance": self.overwrite_importance, "value": "Angle"}
        # Recording and manuel driving
        elif self.memory.memory["Mode1"] == 3:
            if not("Record" in self.memory.overwrite and self.overwrite_importance < self.memory.overwrite["Record"]["importance"]):
                self.memory.memory["Record"] = 1
                self.memory.overwrite["Record"] = {"importance": self.overwrite_importance, "value": 1}
            if not ("Pilot_Mode" in self.memory.overwrite and self.overwrite_importance < self.memory.overwrite["Pilot_Mode"]["importance"]):
                self.memory.memory["Pilot_Mode"] = "Manuel"
                self.memory.overwrite["Pilot_Mode"] = {"importance": self.overwrite_importance, "value": "Manuel"}

    def shut_down(self):
        self.run = False
        logger.info("Stopped")