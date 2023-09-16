from common_functions import PID, Limiter, pwm2float, float2pwm

import logging
import torch
import time
import os
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class Pilot:
    def __init__(self, memory):
        self.memory = memory
        self.thread = None
        self.thread_hz = memory.cfg["DRIVE_LOOP_HZ"]
        self.run = True
        self.outputs = {}
        # It can output steering, throttle and target_speed if pilot equals to Full_Auto or Angle
        self.act_value_type = memory.cfg["ACT_VALUE_TYPE"]
        self.pilot_mode = 0
        self.model_path = None
        self.Steering = 0
        self.Act_Value = 0
        if self.act_value_type == "Speed":
            self.Target_Speed = 0
            self.pid = PID(Kp=memory.cfg["K_PID"]["Kp"], Ki=memory.cfg["K_PID"]["Ki"], Kd=memory.cfg["K_PID"]["Kd"], I_max=memory.cfg["K_PID"]["I_max"])
        self.steering_limiter = Limiter(min_=pwm2float(memory.cfg["STEERING_MIN_PWM"]), max_=pwm2float(memory.cfg["STEERING_MAX_PWM"]))
        self.throttle_limiter = Limiter(min_=pwm2float(memory.cfg["THROTTLE_MIN_PWM"]), max_=pwm2float(memory.cfg["THROTTLE_MAX_PWM"]))
        self.network_input_type = memory.cfg["NETWORK_INPUT_TYPE"]
        self.use_depth = False if self.network_input_type == "RGB" else True

        # Shared memory for multiprocessing
        if "Model_Path" in  memory.memory.keys():
            self.thread = "Multi"
            self.model_path = memory.memory["Model_Path"]
            manager = torch.multiprocessing.Manager()
            self.shared_dict = manager.dict()
            self.shared_dict["run"] = True
            self.shared_dict["pilot_mode"] = 0
            self.shared_dict["cpu_image"] = 0
            if self.use_depth:
                self.shared_dict["depth_image"] = 0
            self.shared_dict["Steering"] = 0
            self.shared_dict["Act_Value"] = 0
        
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
            #logger.info(self.shared_dict["cpu_image"].shape)
            images = self.shared_dict["cpu_image"]
            if self.use_depth:
                depth_image = self.shared_dict["depth_image"]
                depth_array = cv2.cvtColor(depth_image, cv2.COLOR_BGR2GRAY)
                depth_array = depth_array.reshape(images.shape[0], images.shape[1], 1)
                # np.nan_to_num(depth_array, copy=False)
                if self.network_input_type == "D":
                    images = depth_array
                elif self.network_input_type == "RGBD":
                    images = np.concatenate((images, depth_array), axis=2)
                else: 
                    raise Exception("Config settings network_input_type and use_depth contradict each other!")
            model((torch.from_numpy(images.transpose(2, 0, 1))/255).to(device, non_blocking=True).unsqueeze(0))

        logger.info("Warmup Done")
        while self.shared_dict["run"]:
            start_time = time.time()
            if self.shared_dict["pilot_mode"] == "Angle" or self.shared_dict["pilot_mode"] == "Full_Auto":
                # (H x W x C) to (C x H x W) then [0, 1]
                images = self.shared_dict["cpu_image"] 
                if self.use_depth:
                    depth_image = self.shared_dict["depth_image"]
                    depth_array = cv2.cvtColor(depth_image, cv2.COLOR_BGR2GRAY)
                    depth_array = depth_array.reshape(images.shape[0], images.shape[1], 1)
                    # np.nan_to_num(depth_array, copy=False)
                    if self.network_input_type == "D":
                        images = depth_array
                    elif self.network_input_type == "RGBD":
                        images = np.concatenate((images, depth_array), axis=2)
                    else: 
                        raise Exception("Config settings network_input_type and use_depth contradict each other!")

                # Unsqueeze adds dimension to image (batch dimension)
                gpu_image = (torch.from_numpy(images.transpose(2, 0, 1))/255).to(device, non_blocking=True).unsqueeze(0)                
                with torch.no_grad():
                    Steering, Act_Value = model(gpu_image)
                self.shared_dict["Steering"] = Steering.item()
                self.shared_dict["Act_Value"] = Act_Value.item()
            # Inferancing @DRIVE_LOOP_HZ
            sleep_time = 1.0 / self.thread_hz - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        # If we have auto pilot
        if self.model_path:
            self.pilot_mode = self.memory.memory["Pilot_Mode"]
            self.shared_dict["pilot_mode"] = self.pilot_mode
            if self.use_depth:
                self.shared_dict["depth_image"] = self.memory.memory["Depth_Image"]
            self.shared_dict["cpu_image"] = self.memory.memory["Color_Image"]
            if self.pilot_mode == "Angle" or self.pilot_mode == "Full_Auto":
                self.Steering = self.steering_limiter(self.shared_dict["Steering"])
                self.memory.memory["Steering"] = self.Steering
                if self.pilot_mode == "Full_Auto":
                    if self.act_value_type == "Speed":
                        self.Target_Speed = self.shared_dict["Act_Value"] * self.memory.memory["Speed_Factor"]
                        self.memory.memory["Target_Speed"] = self.Target_Speed
                        self.memory.memory["Throttle"] = self.throttle_limiter(self.pid(self.memory.memory["Speed"], self.Target_Speed))
                    elif self.act_value_type == "Throttle":
                        self.memory.memory["Throttle"] = self.throttle_limiter(self.shared_dict["Act_Value"] * self.memory.memory["Speed_Factor"])

    
    def shut_down(self):
        self.run = False
        if self.thread == "Multi":
            self.shared_dict["run"] = False
        time.sleep(0.05)
        logger.info("Stopped")
