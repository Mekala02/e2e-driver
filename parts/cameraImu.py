import cv2

class Camera_IMU:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.outputs = {"img_id": 0, "IMU":0}
        self.big_outputs = {"rgb": 0, "depth": 0, "object_detection": 0}
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
        self.memory.big_memory["rgb"] = self.frame
        self.memory.big_memory["depth"] = self.frame
        self.memory.big_memory["object_detection"] = self.frame