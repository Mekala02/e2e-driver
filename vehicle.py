from threading import Thread
import time

class Vehicle:
    def __init__(self):
        self.parts = []
        self.memory = 0

    def add(self, part):
        self.parts.append(part)
        # Giving memory to part
        part.memory = self.memory

    def start(self):
        for part in self.parts:
            # Adding parts output to the memory
            for output, value in part.outputs.items():
                self.memory.add(output, value)
            if hasattr(part, "big_outputs"):
                for big_output, value in part.big_outputs.items():
                    self.memory.add_big(big_output, value)
            if part.threaded:
                t = Thread(target=part.start_thread, args=(), name=part.__class__.__name__)
                t.daemon = True
                t.start()
            time.sleep(0.01)

    def update(self):
        for part in self.parts:
            part.update()

    def shut_down(self):
        for part in self.parts:
            if callable(getattr(part, "shut_down", None)):
                part.shut_down()