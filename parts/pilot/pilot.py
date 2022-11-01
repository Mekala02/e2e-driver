from parts.pilot.networks import Linear

import math
import time
import torch
import logging
import torchvision.transforms as transforms

logger = logging.getLogger(__name__)

class Pilot:
    def __init__(self, memory):
        self.memory = memory
        self.threaded = False
        self.run = False
        self.outputs = {"Steering": 0, "Throttle": 0}
        self.model_path = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Torch Device: {self.device}")
        try:
            self.model_path = memory.untracked["Model_Folder_Path"]
            self.model = Linear(in_channels=3).to(self.device)
            self.model.load_state_dict(torch.load(self.model_path))
            self.model.eval()
            logger.info(f"Successfully Loaded Model At {self.model_path}")  
        except:
            logger.warning("Can Not Load The Model") 
        logger.info("Successfully Added")  
        self.i = 0
        
    def update(self):
        pilot_mode = self.memory.memory["Pilot_Mode"]
        if self.model_path:
            if pilot_mode == "Angle" or pilot_mode == "Full_Auto":
                image = transforms.ToTensor()(self.memory.big_memory["RGB_Image"])
                image = image.to(device=self.device)
                steering_prediction, throttle_prediction = self.model(image)
                # We made data between -1, 1 when trainig so unpacking thoose to pwm value
                steering_prediction = steering_prediction * 600 + 1500
                throttle_prediction = steering_prediction * 600 + 1500
            if pilot_mode == "Angle":
                self.memory.memory["Steering"] = steering_prediction
            elif pilot_mode == "Full_Auto":
                self.memory.memory["Steering"] = steering_prediction
                self.memory.memory["Throttle"] = throttle_prediction
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
