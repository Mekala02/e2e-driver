import logging

logger = logging.getLogger(__name__)

class Yolo:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.run = True
        self.outputs = {}
        logger.info("Successfully Added")

    def update(self):
        pass

    def shut_down(self):
        self.run = False
        logger.info("Stopped")