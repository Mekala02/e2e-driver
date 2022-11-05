"""
Usage:
    expend_svo.py  <data_dir> (-r | -d)

Options:
  -h --help     Show this screen.
  -r            Rgb Image.
  -d            Depth Image
"""

from docopt import docopt
import json
import pyzed.sl as sl
import cv2
import os


def main():
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]

    rgb_data_path = os.path.join(data_folder, "RGB_Image")
    if not os.path.isdir(rgb_data_path):
        os.mkdir(rgb_data_path)

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
    if (err:=zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
        print(err)
        return

    if(args["-r"]):
        index = 0
        while(True):
            zed.set_svo_position(datas[index]["Zed_Data_Id"])
            if (err:=zed.grab()) == sl.ERROR_CODE.SUCCESS:
                zed.retrieve_image(zed_RGB_Image, sl.VIEW.LEFT)
                rgba_image = zed_RGB_Image.get_data()
                rgb_image = cv2.cvtColor(rgba_image, cv2.COLOR_RGBA2RGB)
                # rgb_image = cv2.resize(rgb_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                cv2.imwrite(os.path.join(rgb_data_path, str(index)+"." + "jpg"), rgb_image)
            elif(err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED):
                print("SVO end has been reached.")
                return
            else:
                print(err)
                return
            index += 1

if __name__ == "__main__":
    main()