"""
Usage:
    train.py  <data_dir>

Options:
  -h --help     Show this screen.
"""

import json
from torch.utils.data import Dataset
import numpy as np
import cv2
import os


class Load_Data(Dataset):
    def __init__(self, data_folder, use_depth_input=False, transform=None):
        self.data_folder_path = data_folder
        self.transform = transform
        self.use_depth_input = use_depth_input
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
        rgb_image = self.load_RGB_image(os.path.join(self.RGB_image_path, str(self.datas[index]["Img_Id"]) + "." + self.RGB_image_format))

        if self.use_depth_input:
            depth_image = self.load_Depth_image(os.path.join(self.Depth_image_path, str(self.datas[index]["Img_Id"]) + "." + self.Depth_image_format))
            depth_image = depth_image.reshape(rgb_image.shape[0], rgb_image.shape[1], 1)
            np.nan_to_num(depth_image, copy=False)
            images = np.concatenate((rgb_image, depth_image), axis=2)
        else:
            images = rgb_image

        other_inputs = np.array([[
            self.datas[index]["IMU_Accel_X"],
            self.datas[index]["IMU_Accel_Y"],
            self.datas[index]["IMU_Accel_Z"],
            self.datas[index]["IMU_Gyro_X"],
            self.datas[index]["IMU_Gyro_Y"],
            self.datas[index]["IMU_Gyro_Z"],
            self.datas[index]["Speed"]
        ]], dtype=np.float32)

        # Making pwm data between -1, 1
        label = np.array([[self.datas[index]["Steering"], self.datas[index]["Throttle"]]], dtype=np.float32)
        label = (label - 1500) / 600

        if self.transform:
            images = self.transform(images)
            other_inputs = self.transform(other_inputs)
            label = self.transform(label)

        return images, other_inputs, label


if __name__ == "__main__":
    from docopt import docopt
    import torchvision.transforms as transforms
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]
    test = Load_Data(data_folder, transforms.ToTensor())
    images, other_inputs, label = test[100]
    print(images.shape)
    print(other_inputs.shape)
    print(label.shape)