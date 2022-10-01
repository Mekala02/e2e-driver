import logging

logger = logging.getLogger(__name__)

class FPS_Counter:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.run = True
        self.outputs = {"Fps": 0}
        
        self.past_time = 0
        self.epsilon = 10 ** -6
        self.counter = 0
        logger.info("Successfully Added")

    def update(self):
        timestamp = self.memory.memory["Timestamp"]
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

        # timestamp = self.memory.memory["timestamp"]
        # self.memory.memory["fps"] = round(1000 / ((timestamp - self.past_time) + self.epsilon))
        # self.past_time = timestamp