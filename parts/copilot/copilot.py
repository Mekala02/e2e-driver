class Copilot:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"Stop": 0, "Taxi": 0, "Direction": "Forward", "Lane": "Right"}

    def update(self):
        pass