"""
Usage:
    expend_svo.py  <data_dir> (--c | --d | --c --d)

Options:
  -h --help     Show this screen.
  --c            Expands Color Image.
  --d            Expands Depth Image.
"""

import multiprocessing as mp
from docopt import docopt
import json
import cv2
import os


def write(data_folder, start, stop, color=False, depth=False):
    index = start
    svo_path = os.path.join(data_folder, "zed_record.svo")
    memory_file_path = os.path.join(data_folder, "memory.json")
    color_data_path = os.path.join(data_folder, "Color_Image")
    depth_data_path = os.path.join(data_folder, "Depth_Image")
    with open(memory_file_path) as data_file:
        datas = json.load(data_file)
    import pyzed.sl as sl
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(svo_path)
    init_parameters.svo_real_time_mode = False
    zed = sl.Camera()
    zed_Color_Image = sl.Mat()
    zed_Depth_Image = sl.Mat()
    if (err:=zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
        print(err)
        return

    print("Procces Started")
    while(index < stop):
        color_image_file = os.path.join(color_data_path, str(datas[index]["Data_Id"])+"." + "jpg")
        depth_image_file = os.path.join(depth_data_path, str(datas[index]["Data_Id"])+"." + "jpg")
        if (color and not os.path.isfile(color_image_file)) or (depth and not os.path.isfile(depth_image_file)):
            zed.set_svo_position(datas[index]["Zed_Data_Id"])
            if (err:=zed.grab()) == sl.ERROR_CODE.SUCCESS:
                if(color):
                    zed.retrieve_image(zed_Color_Image, sl.VIEW.LEFT)
                    color_image = cv2.cvtColor(zed_Color_Image.get_data(), cv2.COLOR_RGBA2RGB)
                    color_image = cv2.resize(color_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                    # Giving data name according to memory.json Zed_Data_Id (not the zed_camera )
                    cv2.imwrite(color_image_file, color_image)
                if(depth):
                    zed.retrieve_image(zed_Depth_Image, sl.VIEW.DEPTH)
                    depth_image = cv2.cvtColor(zed_Depth_Image.get_data(), cv2.COLOR_RGBA2RGB)
                    depth_image = cv2.resize(depth_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                    cv2.imwrite(depth_image_file, depth_image)
            else:
                print(err)
                return
        index += 1
    print("This Process Is Compleated")


def expand(data_folder, datas, color=False, depth=False, num_workers=6):
    color_data_path = os.path.join(data_folder, "Color_Image")
    depth_data_path = os.path.join(data_folder, "Depth_Image")
    if not os.path.isdir(color_data_path):
        os.mkdir(color_data_path)
    if not os.path.isdir(depth_data_path):
        os.mkdir(depth_data_path)

    # config_file_path = os.path.join(data_folder, "cfg.json")
    # with open(config_file_path) as cfg_file:
    #     cfg = json.load(cfg_file)

    quotient, remainder = divmod(len(datas), num_workers)
    processes = []
    start = 0
    stop = quotient
    for i in range(1, num_workers+1):
        # If we have rmainder last one process do extra work
        if i == num_workers:
            stop += remainder
        p = mp.Process(target=write, args=(data_folder, start, stop, color, depth), daemon=True, name=i)
        processes.append(p)
        start +=  quotient
        stop = start + quotient
    for process in processes:
        process.start()
    for process in processes:
        process.join()


if __name__ == "__main__":
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]
    color = args["--c"]
    depth = args["--d"]
    with open(os.path.join(data_folder, "memory.json")) as data_file:
        datas = json.load(data_file)
    expand(data_folder, datas, color=color, depth=depth, num_workers=7)
    