from threading import Thread
import logging
import time

logger = logging.getLogger(__name__)

class Vehicle:
    def __init__(self, memory=0):
        self.parts = []
        self.memory = memory

    def add(self, part):
        self.parts.append(part)

    def start(self):
        logger.info("Starting parts \n")
        for part in self.parts:
            # Adding parts output to the memory
            for output, value in part.outputs.items():
                self.memory.add(output, value)
            if hasattr(part, "big_outputs"):
                for big_output, value in part.big_outputs.items():
                    self.memory.add_big(big_output, value)
            if part.threaded:
                t = Thread(target=part.start_thread, args=(), daemon=True, name=part.__class__.__name__)
                t.start()
            time.sleep(0.02)

    def update(self):
        for part in self.parts:
            part.update()

    def shut_down(self):
        for part in self.parts:
            part.shut_down()
        logger.info("Stopped")