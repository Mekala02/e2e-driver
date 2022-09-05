class Camera_IMU:
    def __init__(self):
        self.threaded = False
        self.memory = 0
        self.outputs = {"Img": 0, "IMU":0}

    def update(self):
        pass