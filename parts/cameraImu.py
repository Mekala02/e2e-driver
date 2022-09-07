from tkinter import Frame
import cv2

from parts.web_server.app import generate_frames

class Camera_IMU:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.outputs = {"img": 0, "IMU":0}
        self.camera=cv2.VideoCapture(0)
        self.frame = 0

    def generate_frames(self):
        success, frame = self.camera.read()
        if not success:
            return "camera_error"
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame=buffer.tobytes()
            
        self.frame = frame
        

    def start_thread(self):
        while True:
            self.generate_frames()

    def update(self):
        self.memory.camera["rgb"] = self.frame