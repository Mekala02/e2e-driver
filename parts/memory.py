class Memory:
    def __init__(self):
        self.memory = {}
        self.big_memory = {}

    def add(self, name, value=0):
        self.memory[name] = value
    
    def add_big(self, name, value=0):
        self.big_memory[name] = value

    def print_memory(self):
        print(self.memory)