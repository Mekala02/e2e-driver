class Arduino:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"speed": 0}
        # If pilot = manuel self.outputs = {"speed": 0, "steering": 0, "throttle": 0}

    def update(self):
        pass