"""
Usage:
    train.py  <data_dir>

Options:
  -h --help     Show this screen.
"""

import json
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms
import pyzed.sl as sl
import logging
import numpy as np
import cv2
import os

logger = logging.getLogger(__name__)


class Load_Data(Dataset):
    def __init__(self, data_folder, use_depth_input=False, use_other_inputs=False):
        self.data_folder_path = data_folder
        self.use_depth_input = use_depth_input
        self.use_other_inputs = use_other_inputs
        self.changes = None

        # Constructing paths
        self.config_file_path = os.path.join(self.data_folder_path, "cfg.json")
        self.changes_file_path = os.path.join(self.data_folder_path, "changes.json")
        self.memory_file_path = os.path.join(self.data_folder_path, "memory.json")
        self.RGB_image_path = os.path.join(self.data_folder_path, "big_data", "RGB_Image")
        self.Depth_image_path = os.path.join(self.data_folder_path, "big_data", "Depth_Image")

        # Opening and reading from files
        with open(self.config_file_path) as cfg_file:
            self.cfg = json.load(cfg_file)
        if os.path.isfile(self.changes_file_path):
            with open(self.changes_file_path) as changes_file:
                self.changes = json.load(changes_file)
        with open(self.memory_file_path) as data_file:
            self.datas = json.load(data_file)

        # Applying changes (came from data_clear_app) to our datas in memory
        if self.changes:
            self.deleted_data_indexes = []
            self.other_changes_indexes = []
            for change_dict in self.changes:
                if "Delete" in change_dict["Changes"]:
                    self.deleted_data_indexes.append(change_dict["Indexes"])
                else:
                    self.other_changes_indexes.append(change_dict["Indexes"])
                    # ToDo made the changes
            self.deleted_data_indexes = np.array(self.deleted_data_indexes)
            self.other_changes_indexes = np.array(self.other_changes_indexes)

            for deleted_indexes in self.deleted_data_indexes:
                self.datas= np.delete(self.datas, [range(deleted_indexes[0], deleted_indexes[1]+1)])

        if self.cfg["SVO_COMPRESSION_MODE"]:
            input_path = os.path.join(data_folder, "zed_record.svo")
            init_parameters = sl.InitParameters()
            init_parameters.set_from_svo_file(input_path)
            self.zed = sl.Camera()
            self.zed_RGB_Image = sl.Mat()
            self.zed_Depth_Map = sl.Mat()
            if (err:=self.zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
                logger.error(err)

        self.RGB_image_format = self.cfg["RGB_IMAGE_FORMAT"]
        self.Depth_image_format = self.cfg["DEPTH_IMAGE_FORMAT"]

        # Constructing image loader functions
        for which_image in ["RGB", "Depth"]:
            img_format = getattr(self, f"{which_image}_image_format")
            if img_format == "npy":
                setattr(self, f"load_{which_image}_image", np.load)
            elif img_format == "npz":
                setattr(self, f"load_{which_image}_image", self.load_npz)
            elif img_format == "jpg" or img_format == "jpeg" or img_format == "png":
                setattr(self, f"load_{which_image}_image", cv2.imread)

    def load_npz(self, path):
        return np.load(path)["arr_0"]

    def __len__(self):
        return(len(self.datas))

    def __getitem__(self, index):
        if self.cfg["SVO_COMPRESSION_MODE"]:
            self.zed.set_svo_position(self.datas[index]["Zed_Data_Id"])
            if (err:=self.zed.grab()) == sl.ERROR_CODE.SUCCESS:
                self.zed.retrieve_image(self.zed_RGB_Image, sl.VIEW.LEFT)
                rgba_image = self.zed_RGB_Image.get_data()
                rgb_image = cv2.cvtColor(rgba_image, cv2.COLOR_RGBA2RGB)
                if self.use_depth_input:
                    self.zed.retrieve_measure(self.zed_Depth_Map, sl.MEASURE.DEPTH)
                    Depth_array = self.zed_Depth_Map.get_data()
            else:
                logger.warning(err)
        else:
            rgb_image = self.load_RGB_image(os.path.join(self.RGB_image_path, str(self.datas[index]["Data_Id"]) + "." + self.RGB_image_format))
            if self.use_depth_input:
                Depth_array = self.load_Depth_image(os.path.join(self.Depth_image_path, str(self.datas[index]["Data_Id"]) + "." + self.Depth_image_format))

        if self.use_depth_input:
            Depth_array = Depth_array.reshape(rgb_image.shape[0], rgb_image.shape[1], 1)
            np.nan_to_num(Depth_array, copy=False)
            images = np.concatenate((rgb_image, Depth_array), axis=2)
        else:
            images = rgb_image
        # Converts numpy.ndarray (H x W x C) in the range [0, 255] to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0] 
        images = transforms.ToTensor()(images)

        if self.use_other_inputs:
            other_inputs = np.array([
                [self.datas[index]["IMU_Accel_X"]],
                [self.datas[index]["IMU_Accel_Y"]],
                [self.datas[index]["IMU_Accel_Z"]],
                [self.datas[index]["IMU_Gyro_X"]],
                [self.datas[index]["IMU_Gyro_Y"]],
                [self.datas[index]["IMU_Gyro_Z"]],
                [self.datas[index]["Speed"]]
            ], dtype=np.float32)
            other_inputs = torch.tensor(other_inputs)

        # Making pwm data between -1, 1
        steering_label = np.array([self.datas[index]["Steering"]], dtype=np.float32)
        throttle_label = np.array([self.datas[index]["Throttle"]], dtype=np.float32)
        steering_label = (steering_label - 1500) / 600
        throttle_label = (throttle_label - 1500) / 600
        steering_label = torch.tensor(steering_label)
        throttle_label = torch.tensor(throttle_label)

        if self.use_other_inputs:
            return images, other_inputs, steering_label, throttle_label
        return images, steering_label, throttle_label


if __name__ == "__main__":
    from docopt import docopt
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]
    test = Load_Data(data_folder)
    images, other_inputs, steering_label, throttle_label = test[100]
    print(images.shape)
    print(other_inputs.shape)
    print(steering_label.shape)
    print(throttle_label.shape)

    print(images.type())
    print(other_inputs.type())
    print(steering_label.type())
    print(throttle_label.type())