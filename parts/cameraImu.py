import cv2

class Camera_IMU:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.outputs = {"IMU_Accel_X": 0, "IMU_Accel_Y": 0, "IMU_Accel_Z": 0, "IMU_Gyro_X": 0, "IMU_Gyro_Y": 0, "IMU_Gyro_Z": 0}
        self.big_outputs = {"RGB": 0, "Depth": 0, "Object_Detection": 0}
        self.camera=cv2.VideoCapture(0+cv2.CAP_DSHOW)
        self.frame = 0

    def generate_frames(self):
        success, frame = self.camera.read()
        if not success:
            return "camera_error"
        else:
            # Frame is a numpy array
            self.frame = frame
        

    def start_thread(self):
        while True:
            self.generate_frames()

    def update(self):
        self.memory.big_memory["RGB"] = self.frame
        self.memory.big_memory["Depth"] = self.frame
        self.memory.big_memory["Object_Detection"] = self.frame