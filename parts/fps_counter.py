import logging

logger = logging.getLogger(__name__)

class FPS_Counter:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {"Fps": 0}
        
        self.past_time = 0
        self.counter = 0
        logger.info("Successfully Added")

    def update(self):
        # Converting ns to ms
        timestamp = self.memory.memory["Timestamp"] * 1e-6
        if timestamp - self.past_time > 1000:
            self.memory.memory["Fps"] = self.counter
            # self.fps_list.append(self.counter)
            self.counter = 0
            self.past_time = timestamp
        else:
            self.counter += 1

    def shut_down(self):
        self.run = False
        logger.info("Stopped")