import logging

logger = logging.getLogger(__name__)

class Yolo:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {"Object_Detection_Image": 0}
        logger.info("Successfully Added")

    def update(self):
        pass

    def shut_down(self):
        self.run = False
        logger.info("Stopped")