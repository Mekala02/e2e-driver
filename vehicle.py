from threading import Thread

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
            for output in part.outputs:
                self.memory.add(output)
            if part.threaded:
                t = Thread(target=part.start_thread, args=())
                t.daemon = True
                t.start()

    def update(self):
        for part in self.parts:
            part.update()