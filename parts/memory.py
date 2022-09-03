class Memory:
    def __init__(self):

        self.memory = {}
            # #Web Server
            # "Camera_Mode": "RGB",
            # "Graph_Mode": "Speed/IMU",
            # "Speed_Factor": 1,
            # "GO": 0,
            # "Record": 0,
            # "Pilot": "Manuel",
            # "Route": "Manuel",
            # # Car
            # "Stop": 0,
            # "Taxi": 0,
            # "Direction": "Forward",
            # "Lane": "Right",
            # "Bar": [0, 0],
            # "Speed": 0,
            # "Graph": []

    def add(self, name, value=0):
        self.memory[name] = value

    def print_memory(self):
        print(self.memory)