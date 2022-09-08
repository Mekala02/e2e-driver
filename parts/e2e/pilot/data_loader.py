"""
Usage:
    data_loader.py  <data_dir>...

Options:
  -h --help     Show this screen.
"""

import sys
import os
sys.path.append(os.path.join(os.path.expanduser('~'), "e2e-driver"))
from common_functions import Image_Loader

from torch.utils.data import Dataset
import numpy as np
import logging
import torch
import json
import cv2

logger = logging.getLogger(__name__)

class Load_Data(Dataset):
    def __init__(self, data_folder_paths, act_value_type="Throttle", transform=None, reduce_fps=False, use_depth=False, network_input_type="RGB", other_inputs=False):
        self.data_folder_paths = data_folder_paths
        self.act_value_type = act_value_type
        self.transform = transform
        self.reduce_fps = reduce_fps
        self.use_depth = use_depth
        self.network_input_type = network_input_type
        self.other_inputs = other_inputs
        self.data_folders = []
        for folder_path in self.data_folder_paths:
            self.data_folders.append(Data_Folder(folder_path, act_value_type=self.act_value_type, transform=self.transform, reduce_fps=self.reduce_fps, use_depth=self.use_depth, network_input_type=self.network_input_type, other_inputs=self.other_inputs))
        self.len_data_fodlers = len(self.data_folders)
        self.lenght = 0
        for datas in self.data_folders:
            self.lenght += len(datas)

    def __len__(self):
        return(self.lenght)

    def __getitem__(self, index):
        folder_index, data_index = self.calculate_index(index)
        if self.other_inputs:
            images, other_inputs, steering_label, act_value_label = self.data_folders[folder_index][data_index]
            return images, other_inputs, steering_label, act_value_label
        images, steering_label, act_value_label = self.data_folders[folder_index][data_index]
        return images, steering_label, act_value_label

    def calculate_index(self, index):
        # If we use one file index will be same
        if self.len_data_fodlers == 1:
            return 0, index
        data_index = index
        # For multiple data files we finding corresponding file no and data index
        for folder_index, datas in enumerate(self.data_folders):
            if data_index < len(datas):
                return folder_index, data_index
            data_index -= len(datas)


class Data_Folder():
    def __init__(self, data_folder_path, act_value_type="Throttle", transform=None, reduce_fps=False, use_depth=False, network_input_type="RGB" ,other_inputs=False):
        self.data_folder_path = data_folder_path
        self.act_value_type = act_value_type
        self.transform = transform
        self.reduce_fps = reduce_fps
        self.use_depth = use_depth
        self.network_input_type = network_input_type
        self.other_inputs = other_inputs
        self.changes = None

        # Constructing paths
        self.config_file_path = os.path.join(self.data_folder_path , "cfg.json")
        self.changes_file_path = os.path.join(self.data_folder_path , "changes.json")
        self.memory_file_path = os.path.join(self.data_folder_path , "memory.json")
        self.Color_Image_folder_path = os.path.join(self.data_folder_path , "Color_Image")
        self.Depth_Image_folder_path = os.path.join(self.data_folder_path , "Depth_Image")

        # Opening and reading from files
        with open(self.config_file_path) as cfg_file:
            self.cfg = json.load(cfg_file)
        if os.path.isfile(self.changes_file_path):
            with open(self.changes_file_path) as changes_file:
                self.changes = json.load(changes_file)
        with open(self.memory_file_path) as data_file:
            self.datas = json.load(data_file)

        if self.act_value_type != self.cfg["ACT_VALUE_TYPE"]:
            logger.warning(f"Training And Config Act Vaule Type Is Different !!!")

        # Applying changes (came from data_clear_app) to our datas in memory
        if self.changes:
            self.deleted_data_indexes = []
            self.other_changes_indexes = []
            for change_dict in self.changes:
                if "Delete" in change_dict["Changes"]:
                    self.deleted_data_indexes.append(change_dict["Indexes"])
                else:
                    for key, value in change_dict["Changes"].items():
                        for i in range(change_dict["Indexes"][0], change_dict["Indexes"][1]):
                            self.datas[i][key] = value
            self.deleted_data_indexes = np.array(self.deleted_data_indexes)
            for deleted_indexes in self.deleted_data_indexes:
                self.datas= np.delete(self.datas, [range(deleted_indexes[0], deleted_indexes[1])])

        if self.reduce_fps:
            # Sampling data according to fps (deleting unnecesary datapoints)
            # Converting nanosecond to second and finding how much time we want
            delta = 1e+9 / self.reduce_fps
            timestamp = 0
            delete_indexes = []
            for index, row in enumerate(self.datas):
                if row["Timestamp"] - timestamp < delta:
                    delete_indexes.append(index)
                else:
                    timestamp = row["Timestamp"]
            self.datas= np.delete(self.datas, delete_indexes)

        self.data_lenght = len(self.datas)

        if self.cfg["SVO_COMPRESSION_MODE"]:
            # We converting SVO data to jpg and saving them then using jpg's for training fast
            # If we not expanded svo, we expanding it.
            if not os.path.isdir(self.Color_Image_folder_path) or (self.use_depth and not os.path.isdir(self.Depth_Image_folder_path)):
                logger.warning("First you have to expand the svo file")
                quit()
                # ToDo: Multiproccesing quits when runned in there, fix it
                # import sys
                # sys.path.append(os.path.join(os.path.expanduser('~'), "e2e-driver", "data"))
                # from expend_svo import expand
                # logger.info("Expanding Svo ...")
                # expand(self.data_folder_path, self.datas, color=True, depth=use_depth, num_workers=6)
            # Overwriting the config data
            self.cfg["COLOR_IMAGE_FORMAT"] = "jpg"
            self.cfg["DEPTH_IMAGE_FORMAT"] = "jpg"

        self.Color_Image_format = self.cfg["COLOR_IMAGE_FORMAT"]
        self.Depth_Image_format = self.cfg["DEPTH_IMAGE_FORMAT"]

        self.color_image_loader = Image_Loader(self.Color_Image_format)
        self.depth_image_loader = Image_Loader(self.Depth_Image_format)

    @staticmethod
    def apply_transforms(image, transforms):
        for type_, F in transforms:
            if type_ == "custom":
                image = F(image=image)
            elif type_ == "albumation":
                # Albumentations uses rgb images so we converting bgr to rgb then reconverting to bgr
                image = cv2.cvtColor(F(image=cv2.cvtColor(image, cv2.COLOR_BGR2RGB))["image"], cv2.COLOR_RGB2BGR)
        return image

    def __len__(self):
        return(self.data_lenght)

    def __getitem__(self, index):
        color_image_path = os.path.join(self.Color_Image_folder_path, str(self.datas[index]["Data_Id"]) + "." + self.Color_Image_format)
        color_image = self.color_image_loader(color_image_path)
        # Applying transforms such as resizing, data augmentation
        if self.transform and self.transform["color_image"]:
            color_image = self.apply_transforms(color_image, self.transform["color_image"])
        
        images = color_image
        if self.use_depth:
            depth_image_path = os.path.join(self.Depth_Image_folder_path, str(self.datas[index]["Data_Id"]) + "." + self.Depth_Image_format)
            depth_image = self.depth_image_loader(depth_image_path)
            if self.transform and self.transform["depth_image"]:
                depth_image = self.apply_transforms(depth_image, self.transform["depth_image"])
            depth_array = cv2.cvtColor(depth_image, cv2.COLOR_BGR2GRAY)
            depth_array = depth_array.reshape(color_image.shape[0], color_image.shape[1], 1)
            # np.nan_to_num(depth_array, copy=False)
            if self.network_input_type == "D":
                images = depth_array
            elif self.network_input_type == "RGBD":
                images = np.concatenate((color_image, depth_array), axis=2)
            else: 
                raise Exception("Config settings network_input_type and use_depth contradict each other!")
        # (H x W x C) to (C x H x W)
        images = images.transpose(2, 0, 1)
        # Making image contiguous on memory
        images = np.ascontiguousarray(images)
        # Not normalizing yet
        images = torch.from_numpy(images)

        if self.other_inputs:
            other_inputs = np.array([[self.datas[index][input]] for input in self.other_inputs], dtype=np.float32)
            other_inputs = torch.from_numpy(other_inputs)

        steering_label = torch.tensor([self.datas[index]["Steering"]], dtype=torch.float)
        if self.act_value_type == "Throttle":
            act_value_label = torch.tensor([self.datas[index]["Throttle"]], dtype=torch.float)
        elif self.act_value_type == "Speed":
            act_value_label = torch.tensor([self.datas[index]["Target_Speed"]], dtype=torch.float)
        elif self.act_value_type == "Encoder_Speed":
            act_value_label = torch.tensor([self.datas[index]["Speed"]], dtype=torch.float)
        else:
            logger.warning("Invalid Act Value Type")

        if self.other_inputs:
            return images, other_inputs, steering_label, act_value_label
        return images, steering_label, act_value_label


if __name__ == "__main__":
    from docopt import docopt
    args = docopt(__doc__)
    data_folders = args["<data_dir>"]
    other_inputs = ["IMU_Accel_X", "IMU_Accel_Y", "IMU_Accel_Z", "IMU_Gyro_X", "IMU_Gyro_Y", "IMU_Gyro_Z", "Speed"]
    test = Load_Data(data_folders, act_value_type="Speed", transform=None, other_inputs=other_inputs, use_depth=False)
    # images, steering_label, act_value_label = test[10]

    images, other_inputs, steering_label, act_value_label = test[10]
    print(images.shape)
    print(other_inputs.shape)
    print(steering_label.shape)
    print(act_value_label.shape)

    print(images.type())
    print(other_inputs.type())
    print(steering_label.type())
    print(act_value_label.type())