class Memory:
    def __init__(self):

        self.memory = {}
        self.camera = {"rgb": 0, "depth": 0, "object_detection": 0}

    def add(self, name, value=0):
        self.memory[name] = value

    def print_memory(self):
        print(self.memory)