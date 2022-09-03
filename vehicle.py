from threading import Thread

class Vehicle:
    def __init__(self, memory):
        self.parts = []
        self.memory = memory

    def add(self, part):
        self.parts.append(part)

    def start(self):
        for part in self.parts:
            # Adding parts output to the memory
            for output in part.outputs:
                self.memory.add(output)
            if part.thread:
                t = Thread(target=part.start_thread, args=())
                t.daemon = True
                t.start()
            else:
                part.start()

    def update(self):
        for part in self.parts:
            part.update()

