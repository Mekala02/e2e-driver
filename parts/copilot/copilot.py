class Copilot:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"stop": 0, "taxi": 0, "direction": "Forward", "lane": "Right"}

    def update(self):
        pass