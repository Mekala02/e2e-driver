import logging

logger = logging.getLogger(__name__)

class Arduino:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.run = True
        self.outputs = {"Speed": 0}
        # If pilot = manuel self.outputs = {"speed": 0, "steering": 0, "throttle": 0}
        logger.info("Successfully Added")

    def update(self):
        pass

    def shut_down(self):
        self.run = False
        logger.info("Successfully Added")