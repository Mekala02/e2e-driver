"""
Usage:
    data_loader.py  <data_dir>...

Options:
  -h --help     Show this screen.
"""

from torch.utils.data import Dataset
import numpy as np
import logging
import torch
import json
import cv2
import os

logger = logging.getLogger(__name__)

class Load_Data(Dataset):
    def __init__(self, data_folder_paths, reduce_resolution=False, reduce_fps=False, use_depth=False, other_inputs=False):
        self.data_folder_paths = data_folder_paths
        self.reduce_resolution = reduce_resolution
        self.reduce_fps = reduce_fps
        self.use_depth = use_depth
        self.other_inputs = other_inputs
        self.data_folders = []
        for folder_path in self.data_folder_paths:
            self.data_folders.append(Data_Folder(folder_path, reduce_resolution=self.reduce_resolution, reduce_fps=self.reduce_fps, use_depth=self.use_depth, other_inputs=self.other_inputs, expend_svo=True))
        self.len_data_fodlers = len(self.data_folders)
        self.lenght = 0
        for datas in self.data_folders:
            self.lenght += len(datas)

    def __len__(self):
        return(self.lenght)

    def __getitem__(self, index):
        folder_index, data_index = self.calculate_index(index)
        if self.other_inputs:
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
    def __init__(self, data_folder_path, reduce_resolution=False, reduce_fps=False, use_depth=False, other_inputs=False, expend_svo=False):
        self.data_folder_path = data_folder_path
        self.reduce_resolution = reduce_resolution
        self.reduce_fps = reduce_fps
        self.use_depth = use_depth
        self.other_inputs = other_inputs
        self.expend_svo = expend_svo
        self.changes = None

        # Constructing paths
        self.config_file_path = os.path.join(self.data_folder_path , "cfg.json")
        self.changes_file_path = os.path.join(self.data_folder_path , "changes.json")
        self.memory_file_path = os.path.join(self.data_folder_path , "memory.json")
        self.Color_Image_path = os.path.join(self.data_folder_path , "Color_Image")
        self.Depth_Image_path = os.path.join(self.data_folder_path , "Depth_Image")

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
            # If we recorded the data to SVO file but want fast training
            # we converting SVO data to jpg and saving them then using jpg's for training
            if self.expend_svo:
                # If our mode is expand_svo but we not expanded svo, we expanding it.
                if not os.path.isdir(self.Color_Image_path) or (self.use_depth and not os.path.isdir(self.Depth_image_path)):
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
            else:
                import pyzed.sl as sl
                input_path = os.path.join(self.data_folder_path, "zed_record.svo")
                init_parameters = sl.InitParameters()
                init_parameters.set_from_svo_file(input_path)
                init_parameters.svo_real_time_mode = False
                self.zed = sl.Camera()
                self.zed_Color_Image = sl.Mat()
                self.zed_Depth_Map = sl.Mat()
                if (err:=self.zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
                    logger.error(err)

        self.Color_Image_format = self.cfg["COLOR_IMAGE_FORMAT"]
        self.Depth_Image_format = self.cfg["DEPTH_IMAGE_FORMAT"]

    def load_Image(self, path, img_format, index):
        if img_format == "npy":
            return np.load(os.path.join(path, str(self.datas[index]["Data_Id"]) + "." + img_format))
        elif img_format == "npz":
            return np.load(os.path.join(path, str(self.datas[index]["Data_Id"]) + "." + img_format))["arr_0"]
        elif self.cfg["SVO_COMPRESSION_MODE"] and not self.expend_svo:
            return load_SVO_data(self, path, index)
        elif img_format == "jpg" or img_format == "jpeg" or img_format == "png" or self.expend_svo:
            return cv2.imread(os.path.join(path, str(self.datas[index]["Data_Id"]) + "." + img_format))
        else:
            logger.warning("Unknown Image Format For Loading")

    def load_SVO_data(self, path, index):
        base_name = os.path.basename(path)
        self.zed.set_svo_position(self.datas[index]["Zed_Data_Id"])
        if (err:=self.zed.grab()) != sl.ERROR_CODE.SUCCESS:
            logger.warning(err)
        else:
            if base_name == "Color_Image":
                self.zed.retrieve_image(self.zed_Color_Image, sl.VIEW.LEFT)
                bgra_image = self.zed_BGR_Image.get_data()
                color_image = cv2.cvtColor(bgra_image, cv2.COLOR_BGRA2BGR)
                return color_image
            elif base_name == "Depth_Image":
                self.zed.retrieve_measure(self.zed_Depth_Map, sl.MEASURE.DEPTH)
                depth_array = self.zed_Depth_Map.get_data()
                return depth_array

    def __len__(self):
        return(self.data_lenght)

    def __getitem__(self, index):
        color_image = self.load_Image(self.Color_Image_path, self.Color_Image_format, index)
        if self.reduce_resolution:
            color_image = cv2.resize(color_image, (self.reduce_resolution["width"], self.reduce_resolution["height"]), interpolation= cv2.INTER_LINEAR)
        images = color_image
        if self.use_depth:
            depth_image = self.load_Image(self.Depth_Image_path, self.Depth_Image_format, index)
            if self.reduce_resolution:
                depth_image = cv2.resize(depth_image, (self.reduce_resolution["width"], self.reduce_resolution["height"]), interpolation= cv2.INTER_LINEAR)
            depth_array = cv2.cvtColor(depth_image, cv2.COLOR_BGR2GRAY)
            depth_array = depth_array.reshape(color_image.shape[0], color_image.shape[1], 1)
            # np.nan_to_num(depth_array, copy=False)
            images = np.concatenate((color_image, depth_array), axis=2)
        # (H x W x C) to (C x H x W)
        images = images.transpose(2, 0, 1)
        # Making image contiguous on memory
        images = np.ascontiguousarray(images)
        # Not normalizing yet
        images = torch.from_numpy(images)

        if self.other_inputs:
            other_inputs = np.array([[self.datas[index][input]] for input in self.other_inputs], dtype=np.float32)
            other_inputs = torch.from_numpy(other_inputs)

        # Making pwm data between -1, 1
        steering_label = (self.datas[index]["Steering"] - 1500) / 500
        throttle_label = (self.datas[index]["Throttle"] - 1500) / 500
        steering_label = torch.tensor([steering_label], dtype=torch.float)
        throttle_label = torch.tensor([throttle_label], dtype=torch.float)

        if self.other_inputs:
            return images, other_inputs, steering_label, throttle_label
        return images, steering_label, throttle_label


if __name__ == "__main__":
    from docopt import docopt
    args = docopt(__doc__)
    data_folders = args["<data_dir>"]
    test = Load_Data(data_folders, other_inputs=True, use_depth=True)
    images, other_inputs, steering_label, throttle_label = test[600]
    print(images.shape)
    print(other_inputs.shape)
    print(steering_label.shape)
    print(throttle_label.shape)

    print(images.type())
    print(other_inputs.type())
    print(steering_label.type())
    print(throttle_label.type())