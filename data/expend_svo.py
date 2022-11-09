"""
Usage:
    expend_svo.py  <data_dir> (--r | --d | --r --d)

Options:
  -h --help     Show this screen.
  --r            Expands Rgb Image.
  --d            Expands Depth Image.
"""

from docopt import docopt
import pyzed.sl as sl
import json
import cv2
import os


def main():
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]

    rgb_data_path = os.path.join(data_folder, "RGB_Image")
    if not os.path.isdir(rgb_data_path):
        os.mkdir(rgb_data_path)

    depth_data_path = os.path.join(data_folder, "Depth_Image")
    if not os.path.isdir(depth_data_path):
        os.mkdir(depth_data_path)

    config_file_path = os.path.join(data_folder, "cfg.json")
    memory_file_path = os.path.join(data_folder, "memory.json")
    with open(config_file_path) as cfg_file:
        cfg = json.load(cfg_file)
    with open(memory_file_path) as data_file:
        datas = json.load(data_file)

    svo_path = os.path.join(data_folder, "zed_record.svo")
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(svo_path)
    init_parameters.svo_real_time_mode = False
    zed = sl.Camera()
    zed_RGB_Image = sl.Mat()
    zed_Depth_Image = sl.Mat()
    if (err:=zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
        print(err)
        return

    index = 0
    while(True):
        zed.set_svo_position(datas[index]["Zed_Data_Id"])
        if (err:=zed.grab()) == sl.ERROR_CODE.SUCCESS:
            if(args["--r"]):
                zed.retrieve_image(zed_RGB_Image, sl.VIEW.LEFT)
                rgb_image = cv2.cvtColor(zed_RGB_Image.get_data(), cv2.COLOR_RGBA2RGB)
                rgb_image = cv2.resize(rgb_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                # Giving data name according to memory.json Zed_Data_Id (not the zed_camera )
                cv2.imwrite(os.path.join(rgb_data_path, str(datas[index]["Data_Id"])+"." + "jpg"), rgb_image)
            if(args["--d"]):
                zed.retrieve_image(zed_Depth_Image, sl.VIEW.DEPTH)
                depth_image = cv2.cvtColor(zed_Depth_Image.get_data(), cv2.COLOR_RGBA2RGB)
                depth_image = cv2.resize(depth_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                cv2.imwrite(os.path.join(depth_data_path, str(datas[index]["Data_Id"])+"." + "jpg"), depth_image)
        elif(err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED):
            print("SVO end has been reached.")
            return
        else:
            print(err)
            return
        index += 1

if __name__ == "__main__":
    main()