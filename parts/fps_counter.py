class FPS_Counter:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"fps": 0}
        self.past_time = 0
        self.epsilon = 10 ** -6 

    def update(self):
        timestamp = self.memory.memory["timestamp"]
        self.memory.memory["fps"] = round(1000 / ((timestamp - self.past_time) + self.epsilon))
        self.past_time = timestamp