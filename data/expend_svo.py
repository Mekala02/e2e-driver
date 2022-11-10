"""
Usage:
    expend_svo.py  <data_dir> (--r | --d | --r --d)

Options:
  -h --help     Show this screen.
  --r            Expands Rgb Image.
  --d            Expands Depth Image.
"""

import multiprocessing as mp
from docopt import docopt
import json
import cv2
import os

def expand(data_folder, start, stop, rgb=False, depth=False):
    index = start
    svo_path = os.path.join(data_folder, "zed_record.svo")
    memory_file_path = os.path.join(data_folder, "memory.json")
    rgb_data_path = os.path.join(data_folder, "RGB_Image")
    depth_data_path = os.path.join(data_folder, "Depth_Image")
    with open(memory_file_path) as data_file:
        datas = json.load(data_file)
    import pyzed.sl as sl
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(svo_path)
    init_parameters.svo_real_time_mode = False
    zed = sl.Camera()
    zed_RGB_Image = sl.Mat()
    zed_Depth_Image = sl.Mat()
    if (err:=zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
        print(err)
        return

    print("Procces Started")
    while(index < stop):
        zed.set_svo_position(datas[index]["Zed_Data_Id"])
        if (err:=zed.grab()) == sl.ERROR_CODE.SUCCESS:
            if(rgb):
                zed.retrieve_image(zed_RGB_Image, sl.VIEW.LEFT)
                rgb_image = cv2.cvtColor(zed_RGB_Image.get_data(), cv2.COLOR_RGBA2RGB)
                rgb_image = cv2.resize(rgb_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                # Giving data name according to memory.json Zed_Data_Id (not the zed_camera )
                cv2.imwrite(os.path.join(rgb_data_path, str(datas[index]["Data_Id"])+"." + "jpg"), rgb_image)
            if(depth):
                zed.retrieve_image(zed_Depth_Image, sl.VIEW.DEPTH)
                depth_image = cv2.cvtColor(zed_Depth_Image.get_data(), cv2.COLOR_RGBA2RGB)
                depth_image = cv2.resize(depth_image, (160, 120), interpolation= cv2.INTER_LINEAR)
                cv2.imwrite(os.path.join(depth_data_path, str(datas[index]["Data_Id"])+"." + "jpg"), depth_image)
        else:
            print(err)
            return
        index += 1
    print("This Process Is Compleated")


if __name__ == "__main__":
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]
    rgb = args["--r"]
    depth = args["--d"]

    rgb_data_path = os.path.join(data_folder, "RGB_Image")
    if not os.path.isdir(rgb_data_path):
        os.mkdir(rgb_data_path)

    depth_data_path = os.path.join(data_folder, "Depth_Image")
    if not os.path.isdir(depth_data_path):
        os.mkdir(depth_data_path)

    # config_file_path = os.path.join(data_folder, "cfg.json")
    # with open(config_file_path) as cfg_file:
    #     cfg = json.load(cfg_file)

    process_count = 7

    with open(os.path.join(data_folder, "memory.json")) as data_file:
        datas = json.load(data_file)
    
    quotient, remainder = divmod(len(datas), process_count)
    
    processes = []
    start = 0
    stop = quotient
    for i in range(1, process_count+1):
        # If we have rmainder last one process do extra work
        if i == process_count:
            stop += remainder
        p = mp.Process(target=expand, args=(data_folder, start, stop, rgb, depth), daemon=True, name=i)
        processes.append(p)
        start +=  quotient
        stop = start + quotient

    for process in processes:
        process.start()
    for process in processes:
        process.join()
    