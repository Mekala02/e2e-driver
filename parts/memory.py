class Memory:
    def __init__(self):
        # Stores small data like imu steering ...
        self.memory = {}
        # Stores data like save folder name
        self.untracked = {}
        # If some part wants to change value but that value is not its output we add
        # that change to overwrite then when owner that value see the overwrite value
        # It will change the value accordingly
        # Use pop when reading inside owner !!! Othervise it will always overwrite last overwrite value (pop deletes it)
        self.overwrite = {}

    def add(self, name, value=0):
        self.memory[name] = value

    def print_memory(self):
        print(self.memory)