from parts.pilot.networks import Linear
from config import config as cfg

import math
import time
import torch
import logging
import torchvision.transforms as transforms
import cv2

logger = logging.getLogger(__name__)

class Pilot:
    def __init__(self, memory):
        self.memory = memory
        self.threaded = True
        self.run = True
        self.outputs = {"Steering": 0, "Throttle": 0}

        self.model_path = None
        self.pilot_mode = 0
        self.image = 0
        self.transform_image = transforms.ToTensor()
        self.steering_prediction = 0
        self.throttle_prediction = 0

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Torch Device: {self.device}")
        if "Model_Folder_Path" in  memory.untracked.keys():
            # self.model = Linear(in_channels=3).to(self.device)
            # self.model.load_state_dict(torch.load(self.model_path))
            self.model_path = memory.untracked["Model_Folder_Path"]
            self.model = torch.jit.load(self.model_path)
            self.model.eval()
            logger.info(f"Successfully Loaded Model At {self.model_path}")  
        logger.info("Successfully Added")  
        self.i = 0
    
    def predict(self):
        # start_time = time.time()
        rgb_image = cv2.resize(self.image, (160, 120), interpolation= cv2.INTER_LINEAR)
        rgb_image = rgb_image.transpose(2, 0, 1)
        rgb_image = torch.from_numpy(rgb_image)
        # logger.info(f"Transform to tensor: {time.time() - start_time}")
        # start_time = time.time()
        rgb_image = rgb_image.to(self.device, non_blocking=True) / 255.0
        # logger.info(f"To device: {time.time() - start_time}")
        rgb_image = rgb_image.view(1, 3, 160, 120)
        # start_time = time.time()
        with torch.no_grad():
            self.steering_prediction, self.throttle_prediction = self.model(rgb_image)
        # logger.info(f"Prediction: {time.time() - start_time}")
        # We made data between -1, 1 when trainig so unpacking thoose to pwm value
        # self.steering_prediction = int(steering_prediction * 600 + 1500)
        # self.throttle_prediction = int(throttle_prediction * 600 + 1500)

    def start_thread(self):
        logger.info("Starting Thread")
        while self.run:
            start_time = time.time()
            if self.pilot_mode == "Angle" or self.pilot_mode == "Full_Auto":
                self.predict()
            sleep_time = 1.0 / cfg["CAMERA_FPS"] - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)
            # logger.info(1.0 / (time.time() - start_time))

    def update(self):
        self.pilot_mode = self.memory.memory["Pilot_Mode"]
        self.image = self.memory.big_memory["RGB_Image"]
        if self.model_path:
            if self.steering_prediction > cfg["STEERING_MAX_PWM"]: self.steering_prediction=cfg["STEERING_MAX_PWM"]
            if self.steering_prediction < cfg["STEERING_MIN_PWM"]: self.steering_prediction=cfg["STEERING_MIN_PWM"]
            if self.pilot_mode == "Angle":
                self.memory.memory["Steering"] = self.steering_prediction
            elif self.pilot_mode == "Full_Auto":
                self.memory.memory["Steering"] = self.steering_prediction
                self.memory.memory["Throttle"] = self.throttle_prediction
        else:
            # Sin vave for testing web server
            if self.memory.memory["Pilot_Mode"] == "Angle":
                self.memory.memory["Steering"] = int(1500 + math.sin(time.time()) * 600)
            elif self.memory.memory["Pilot_Mode"] == "Full_Auto":
                self.memory.memory["Throttle"] = int(1500 + math.sin(time.time() + 2) * 600)
                self.memory.memory["Steering"] = int(1500 + math.sin(time.time()) * 600)

    def shut_down(self):
        self.run = False
        logger.info("Stopped")
