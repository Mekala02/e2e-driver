"""
Usage:
    data_loader.py  <data_dir>...

Options:
  -h --help     Show this screen.
"""

import json
import torch
from torch.utils.data import Dataset
import pyzed.sl as sl
import logging
import numpy as np
import cv2
import os

logger = logging.getLogger(__name__)

class Load_Data(Dataset):
    def __init__(self, data_folder_paths, use_depth_input=False, use_other_inputs=False):
        self.data_folder_paths = data_folder_paths
        self.use_depth_input = use_depth_input
        self.use_other_inputs = use_other_inputs
        self.data_folders = []
        for folder_path in self.data_folder_paths:
            self.data_folders.append(Data_Folder(folder_path, use_depth_input=self.use_depth_input, use_other_inputs=self.use_other_inputs, expend_svo=True))
        self.len_data_fodlers = len(self.data_folders)
        self.lenght = 0
        for datas in self.data_folders:
            self.lenght += len(datas)

    def __len__(self):
        return(self.lenght)

    def __getitem__(self, index):
        folder_index, data_index = self.calculate_index(index)
        if self.use_other_inputs:
            images, other_inputs, steering_label, throttle_label = self.data_folders[folder_index][data_index]
            return images, other_inputs, steering_label, throttle_label
        images, steering_label, throttle_label = self.data_folders[folder_index][data_index]
        return images, steering_label, throttle_label

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
    def __init__(self, data_folder_path, use_depth_input=False, use_other_inputs=False, expend_svo=False):
        self.data_folder_path = data_folder_path
        self.use_depth_input = use_depth_input
        self.use_other_inputs = use_other_inputs
        self.expend_svo = expend_svo
        self.changes = None

        # Constructing paths
        self.config_file_path = os.path.join(self.data_folder_path , "cfg.json")
        self.changes_file_path = os.path.join(self.data_folder_path , "changes.json")
        self.memory_file_path = os.path.join(self.data_folder_path , "memory.json")
        self.RGB_image_path = os.path.join(self.data_folder_path , "RGB_Image")
        self.Depth_image_path = os.path.join(self.data_folder_path , "Depth_Image")

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

        self.data_lenght = len(self.datas)

        if self.cfg["SVO_COMPRESSION_MODE"]:
            # If we recorded the data to SVO file but want fast training
            # we converting SVO data to jpg and saving them then using jpg's for training
            if not self.expend_svo:
                input_path = os.path.join(self.data_folder_path, "zed_record.svo")
                init_parameters = sl.InitParameters()
                init_parameters.set_from_svo_file(input_path)
                init_parameters.svo_real_time_mode = False
                self.zed = sl.Camera()
                self.zed_RGB_Image = sl.Mat()
                self.zed_Depth_Map = sl.Mat()
                if (err:=self.zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
                    logger.error(err)
            else:
                if not os.path.isdir(self.RGB_image_path):
                    logger.error(f"Can't Open Folder {self.RGB_image_path}")
                    quit()
                # Overwriting the config data
                self.cfg["RGB_IMAGE_FORMAT"] = "jpg"

        self.RGB_image_format = self.cfg["RGB_IMAGE_FORMAT"]
        self.Depth_image_format = self.cfg["DEPTH_IMAGE_FORMAT"]

        # Constructing image loader functions
        for which_image in ["RGB", "Depth"]:
            img_format = getattr(self, f"{which_image}_image_format")
            if img_format == "npy":
                setattr(self, f"load_{which_image}_image", self.load_npy)
            elif img_format == "npz":
                setattr(self, f"load_{which_image}_image", self.load_npz)
            elif self.cfg["SVO_COMPRESSION_MODE"] and not self.expend_svo:
                setattr(self, f"load_{which_image}_image", self.load_SVO_data)
            elif img_format == "jpg" or img_format == "jpeg" or img_format == "png" or self.expend_svo:
                setattr(self, f"load_{which_image}_image", self.load_jpg)
            else:
                logger.warning("Unknown Image Format For Saving")
            
    def load_npy(self, path, index):
        base_name = os.path.basename(path)
        if base_name == "RGB_Image":
            img_format = self.RGB_image_format
        elif base_name == "Depth_Image":
            img_format = self.Depth_image_format
        return np.load(os.path.join(path, str(self.datas[index]["Data_Id"]) + "." + img_format))

    def load_jpg(self, path, index):
        base_name = os.path.basename(path)
        if base_name == "RGB_Image":
            img_format = self.RGB_image_format
        elif base_name == "Depth_Image":
            img_format = self.Depth_image_format
        return cv2.imread(os.path.join(path, str(self.datas[index]["Data_Id"]) + "." + img_format))

    def load_npz(self, path, index):
        base_name = os.path.basename(path)
        if base_name == "RGB_Image":
            img_format = self.RGB_image_format
        elif base_name == "Depth_Image":
            img_format = self.Depth_image_format
        return np.load(os.path.join(path, str(self.datas[index]["Data_Id"]) + "." + img_format))["arr_0"]

    def load_SVO_data(self, path, index):
        base_name = os.path.basename(path)
        self.zed.set_svo_position(self.datas[index]["Zed_Data_Id"])
        if (err:=self.zed.grab()) != sl.ERROR_CODE.SUCCESS:
            logger.warning(err)
        else:
            if base_name == "RGB_Image":
                self.zed.retrieve_image(self.zed_RGB_Image, sl.VIEW.LEFT)
                rgba_image = self.zed_RGB_Image.get_data()
                rgb_image = cv2.cvtColor(rgba_image, cv2.COLOR_RGBA2RGB)
                return rgb_image
            elif base_name == "Depth_Image":
                self.zed.retrieve_measure(self.zed_Depth_Map, sl.MEASURE.DEPTH)
                depth_array = self.zed_Depth_Map.get_data()
                return depth_array

    def __len__(self):
        return(self.data_lenght)

    def __getitem__(self, index):
        rgb_image = self.load_RGB_image(self.RGB_image_path, index)
        rgb_image = cv2.resize(rgb_image, (160, 120), interpolation= cv2.INTER_LINEAR)
        images = rgb_image
        if self.use_depth_input:
            depth_image = self.load_Depth_image(self.Depth_image_path, index)
            depth_image = cv2.resize(depth_image, (160, 120), interpolation= cv2.INTER_LINEAR)
            depth_array = cv2.cvtColor(depth_image, cv2.COLOR_BGR2GRAY)
            depth_array = depth_array.reshape(rgb_image.shape[0], rgb_image.shape[1], 1)
            # np.nan_to_num(depth_array, copy=False)
            images = np.concatenate((rgb_image, depth_array), axis=2)
        # (H x W x C) to (C x H x W)
        images = images.transpose(2, 0, 1)
        # Making image contiguous on memory
        images = np.ascontiguousarray(images)
        # Not normalizing yet
        images = torch.from_numpy(images)

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
            other_inputs = torch.from_numpy(other_inputs)

        # Making pwm data between -1, 1
        steering_label = (self.datas[index]["Steering"] - 1500) / 500
        throttle_label = (self.datas[index]["Throttle"] - 1500) / 500
        steering_label = torch.tensor([steering_label], dtype=torch.float)
        throttle_label = torch.tensor([throttle_label], dtype=torch.float)

        if self.use_other_inputs:
            return images, other_inputs, steering_label, throttle_label
        return images, steering_label, throttle_label


if __name__ == "__main__":
    from docopt import docopt
    args = docopt(__doc__)
    data_folders = args["<data_dir>"]
    test = Load_Data(data_folders, use_other_inputs=True, use_depth_input=True)
    images, other_inputs, steering_label, throttle_label = test[600]
    print(images.shape)
    print(other_inputs.shape)
    print(steering_label.shape)
    print(throttle_label.shape)

    print(images.type())
    print(other_inputs.type())
    print(steering_label.type())
    print(throttle_label.type())