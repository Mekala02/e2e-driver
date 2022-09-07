class FPS_Counter:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"fps": 0}
        self.past_time = 0
        self.epsilon = 10 ** -6
        self.counter = 0

    def update(self):
        timestamp = self.memory.memory["timestamp"]
        if timestamp - self.past_time > 1000:
            self.memory.memory["fps"] = self.counter
            # self.fps_list.append(self.counter)
            self.counter = 0
            self.past_time = timestamp
        else:
            self.counter += 1


        # timestamp = self.memory.memory["timestamp"]
        # self.memory.memory["fps"] = round(1000 / ((timestamp - self.past_time) + self.epsilon))
        # self.past_time = timestamp