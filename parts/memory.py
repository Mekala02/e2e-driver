class Memory:
    def __init__(self):
        # Stores small data like imu steering ...
        self.memory = {}
        # Stores reletively big data like image, depth_array
        self.big_memory = {}
        # Stores data like save folder name
        self.untracked = {}

    def add(self, name, value=0):
        self.memory[name] = value
    
    def add_big(self, name, value=0):
        self.big_memory[name] = value

    def print_memory(self):
        print(self.memory)