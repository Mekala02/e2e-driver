import logging

logger = logging.getLogger(__name__)

class Mode_Selector:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {}
        self.overwrite_importance = 1
        self.overwrites = {"Record", "Pilot_Mode"}

        self.use_DAgger = True if "Model_Path" in self.memory.memory and memory.cfg["USE_DAGGER"] else False
        logger.info("Successfully Added")

    def update(self):
        # If our importance is higher then current overwrite giving permission to overwrite
        overwrite_record = "Record" not in self.memory.memory["Overwrites"] or self.overwrite_importance >= self.memory.memory["Overwrites"]["Record"]["importance"]
        overwrite_pilot_mode = "Pilot_Mode" not in self.memory.memory["Overwrites"] or self.overwrite_importance >= self.memory.memory["Overwrites"]["Pilot_Mode"]["importance"]
        if self.use_DAgger:
            # Not recording and manuel mode
            if self.memory.memory["Mode1"] == 1:
                if overwrite_record:
                    self.memory.memory["Record"] = 0
                    self.memory.memory["Overwrites"]["Record"] = {"value": 0, "importance": self.overwrite_importance}
                if overwrite_pilot_mode:
                    self.memory.memory["Pilot_Mode"] = "Manuel"
                    self.memory.memory["Overwrites"]["Pilot_Mode"] = {"value": "Manuel", "importance": self.overwrite_importance}
            # Not recording and angle mode
            elif self.memory.memory["Mode1"] == 2:
                if overwrite_record:
                    self.memory.memory["Record"] = 0
                    self.memory.memory["Overwrites"]["Record"] = {"value": 0, "importance": self.overwrite_importance}
                if overwrite_pilot_mode:
                    self.memory.memory["Pilot_Mode"] = "Angle"
                    self.memory.memory["Overwrites"]["Pilot_Mode"] = {"value": "Angle", "importance": self.overwrite_importance}
            # Recording and manuel mode
            elif self.memory.memory["Mode1"] == 3:
                if overwrite_record:
                    self.memory.memory["Record"] = 1
                    self.memory.memory["Overwrites"]["Record"] = {"value": 1, "importance": self.overwrite_importance}
                if overwrite_pilot_mode:
                    self.memory.memory["Pilot_Mode"] = "Manuel"
                    self.memory.memory["Overwrites"]["Pilot_Mode"] = {"value": "Manuel", "importance": self.overwrite_importance}
        else:
            # Not Recording
            if self.memory.memory["Mode1"] == 2:
                if overwrite_record:
                    self.memory.memory["Record"] = 0
                    self.memory.memory["Overwrites"]["Record"] = {"value": 0, "importance": self.overwrite_importance}
            # Recording
            elif self.memory.memory["Mode1"] == 3:
                if overwrite_record:
                    self.memory.memory["Record"] = 1
                    self.memory.memory["Overwrites"]["Record"] = {"value": 1, "importance": self.overwrite_importance}

    def shut_down(self):
        self.run = False
        logger.info("Stopped")