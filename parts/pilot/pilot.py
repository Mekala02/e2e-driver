from parts.pilot.networks import Linear
from config import config as cfg

import os
import time
import torch
import logging

logger = logging.getLogger(__name__)

class Pilot:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.run = True
        self.outputs = {"Steering": 0, "Throttle": 0}
        self.pilot_mode = 0
        self.model_path = None

        # Shared memory for multiprocessing
        if "Model_Folder_Path" in  memory.untracked.keys():
            self.thread = "Multi"
            self.model_path = memory.untracked["Model_Folder_Path"]
            manager = torch.multiprocessing.Manager()
            self.shared_dict = manager.dict()
            self.shared_dict["run"] = True
            self.shared_dict["pilot_mode"] = 0
            self.shared_dict["cpu_image"] = 0
            self.shared_dict["steering"] = 0
            self.shared_dict["throttle"] = 0
        
        self.steering = 0
        self.throttle = 0
        
        logger.info("Successfully Added")
    
    def start_process(self):
        # Since it is a new procces we need to reconfigure the logger
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: @ %(name)s %(message)s")
        logger.info("Starting Process")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Device: {device}")
        # Getting model extension
        model_extension = os.path.splitext(os.path.split(self.model_path)[1])[1]
        if model_extension == ".jit":
            model = torch.jit.load(self.model_path).to(device)
        if model_extension == ".trt":
            from torch2trt import TRTModule
            model = TRTModule()
            model.load_state_dict(torch.load(self.model_path))
        logger.info(f"Successfully Loaded Model From {self.model_path}")
        model.eval()
        # First pass is slow so we are warming up
        logger.info("Warming Up The Model...")
        with torch.no_grad():
            model(torch.ones((1, 3, 120, 160), device=device))
        logger.info("Warmup Done")
        while self.shared_dict["run"]:
            start_time = time.time()
            if self.shared_dict["pilot_mode"] == "Angle" or self.shared_dict["pilot_mode"] == "Full_Auto":
                color_image = torch.from_numpy(self.shared_dict["cpu_image"].transpose(2, 0, 1)) / 255
                gpu_image = color_image.to(device, non_blocking=True).view(1, 3, 120, 160)
                with torch.no_grad():
                    steering, throttle = model(gpu_image)
                # We made data between -1, 1 when trainig so unpacking thoose to pwm value
                self.shared_dict["steering"] = int(steering * 500 + 1500)
                self.shared_dict["throttle"] = int(throttle * 500 + 1500)
            # Inferancing @100fps
            sleep_time = 1.0 / 100 - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        # If we have pilot (neurl network)
        if self.model_path:
            self.pilot_mode = self.memory.memory["Pilot_Mode"]
            self.shared_dict["pilot_mode"] = self.pilot_mode
            self.shared_dict["cpu_image"] = self.memory.big_memory["Color_Image"]
            if self.pilot_mode == "Angle" or self.pilot_mode == "Full_Auto":
                self.steering = self.shared_dict["steering"]
                self.throttle = self.shared_dict["throttle"]
                if self.steering > cfg["STEERING_MAX_PWM"]: self.steering=cfg["STEERING_MAX_PWM"]
                if self.steering < cfg["STEERING_MIN_PWM"]: self.steering=cfg["STEERING_MIN_PWM"]
                if self.pilot_mode == "Angle":
                    self.memory.memory["Steering"] = self.steering
                elif self.pilot_mode == "Full_Auto":
                    self.memory.memory["Steering"] = self.steering
                    self.memory.memory["Throttle"] = self.throttle

    def shut_down(self):
        self.run = False
        self.shared_dict["run"] = False
        logger.info("Stopped")
