class Yolo:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.run = True
        self.outputs = {}

    def update(self):
        pass

    def shut_down(self):
        self.run = False