import torch.multiprocessing as mp
from threading import Thread
import logging
import time

logger = logging.getLogger(__name__)

class Vehicle:
    def __init__(self, memory=0):
        self.parts = []
        self.memory = memory
        
        try:
            mp.set_start_method('spawn', force=True)
            logger.info("Multiprocessing Start methot: spawn")
        except RuntimeError:
            logger.error("Cannot Set Start Methot To spawn")

    def add(self, part):
        self.parts.append(part)

    def start(self):
        logger.info("Starting parts \n")
        for part in self.parts:
            # Adding parts output to the memory
            for output, value in part.outputs.items():
                self.memory.add(output, value)
            if part.thread == "Single":
                t = Thread(target=part.start_thread, args=(), daemon=True, name=part.__class__.__name__)
                t.start()
            if part.thread == "Multi":
                p = mp.Process(target=part.start_process, args=(), daemon=True, name=part.__class__.__name__)
                p.start()
            time.sleep(0.02)
        time.sleep(1)

    def update(self):
        for part in self.parts:
            part.update()

    def shut_down(self):
        for part in self.parts:
            part.shut_down()
            time.sleep(0.05)
        logger.info("Stopped")