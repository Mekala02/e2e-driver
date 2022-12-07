"""
Usage:
    data_cleaner_app.py  <data_dir> [--edit_changes] [--expended_svo]

Options:
  -h --help         Show this screen.
  <data_dir>        Data directory
  --edit_changes    Loads server with previously made changes
  --expended_svo    Loads from expended svo folder
"""

import sys
import os
sys.path.append(os.path.join(os.path.expanduser('~'), "e2e-driver"))
from common_functions import Image_Loader

from flask import Flask, render_template, Response, request, jsonify
from waitress import serve
from docopt import docopt
import numpy as np
import threading
import logging
import json
import time
import cv2

app=Flask(__name__)
# Servers memory
data = {}

def generate_frames():
    while True:
        # Geeting img id according to our data index (cursor on the bar)
        data_id = datas[client_outputs["Data_Index"]]["Data_Id"]
        # Getting camera mode (Color_Image, Depth_Image, Object_Detection)
        camera_mode = client_outputs["Camera_Mode"]
        if camera_mode == "Color_Image":
            if Color_Image_format == "svo":
                zed_data_id = datas[client_outputs["Data_Index"]]["Zed_Data_Id"]
                frame = color_image_loader(0, zed_data_id, "Color_Image")
            else:
                color_image_path = os.path.join(Color_Image_folder_path, str(data_id) + "." + Color_Image_format)
                frame = color_image_loader(color_image_path)
        elif camera_mode == "Depth_Image":
            if Color_Image_format == "svo":
                zed_data_id = datas[client_outputs["Data_Index"]]["Zed_Data_Id"]
                frame = depth_image_loader(0, zed_data_id, "Depth_Image")
            else:
                depth_image_path = os.path.join(Depth_Image_folder_path, str(data_id) + "." + Depth_Image_format)
                frame = depth_image_loader(depth_image_path)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # While loop is too fast we need to slow down interval is 4ms (250fps)
        time.sleep(0.004)

@app.route('/')
def index():
    # Rendering template, and sending necessary data to client side
    return render_template('data_cleaner_main.html',  outputs={**client_outputs})

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/outputs', methods=['GET', 'POST'])
def receive_outputs():
    # Receiving servers outputs such as camera mode etc.
    information = request.get_json()
    for key in information.keys():
        # Updating server side (Python)
        client_outputs[key] = information[key]
    return information

search_results = []
@app.route('/search', methods=['GET', 'POST'])
def receive_search():
    # Finding requested search results
    search_phrase = request.get_json()
    # Deleting whitespaces
    search_phrase = search_phrase.replace(" ", "")
    # Clearing the previous search results
    search_results.clear()
    delimiters = ["==", ">=", "<=", ">", "<"]
    for delimiter in delimiters:
        try:
            name, value = search_phrase.split(delimiter)
            # Making first letter capital becaouse our datas starts with capital letter
            name = name.capitalize()
            value = value.capitalize()
            if value.isnumeric():
                value = int(value)
            symbol = delimiter
            break
        except:
            pass
    if symbol == "==":
        for row in datas:
            if row[name] == value:
                search_results.append(row["Data_Id"])
    elif symbol == ">=":
        for row in datas:
            if row[name] >= value:
                search_results.append(row["Data_Id"])
    elif symbol == "<=":
        for row in datas:
            if row[name] <= value:
                search_results.append(row["Data_Id"])
    elif symbol == ">":
        for row in datas:
            if row[name] > value:
                search_results.append(row["Data_Id"])
    elif symbol == "<":
        for row in datas:
            if row[name] < value:
                search_results.append(row["Data_Id"])
    return "a"

@app.route('/search_results')
# Sends search results
def send_search_results():
    return jsonify(search_results)

# Sends data according to our data index (cursor on the bar)
@app.route('/inputs')
def send_inputs():
    data = datas[client_outputs["Data_Index"]]
    return jsonify(data)

# Sends graphs data
@app.route('/graph')
def send_graph():
    send = {}
    # Looping over graphs requests
    for mode in client_outputs["Graph1_Mode"]:
        send[mode] = []
    # Img id is X coordinate of the graph
    send["Data_Id"] = []
    for row in datas:
        # Looping over all dataset and adding neccesry inputs
        send["Data_Id"].append(row["Data_Id"])
        for mode in client_outputs["Graph1_Mode"]:
            send[mode].append(row[mode])
    return jsonify(send)

@app.route('/save', methods=['GET', 'POST'])
def save_changes():
    save = request.get_json()
    if save:
        changes_path = os.path.join(data_folder, "changes.json")
        try:
            os.remove(changes_path)
        except:
            pass
        opened_file = open(changes_path, "w+")
        json.dump(client_outputs["Select_List"], opened_file)
        opened_file.close()
    return "a"

def server_thread():
    serve(app, host="0.0.0.0", port=8080)

if __name__=="__main__":
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]
    folder_name = os.path.basename(data_folder)
    logger = logging.getLogger(__name__)
    json_path = os.path.join(data_folder, "memory.json")
    cfg_path = os.path.join(data_folder, "cfg.json")
    with open(cfg_path) as cfg_file:
        cfg = json.load(cfg_file)
    with open(json_path) as data_file:
        datas = json.load(data_file)
    # Default values for server startup
    client_outputs = {"Data_Lenght": len(datas), "Data_Index": 0, "Data_Folder": folder_name,
    "Left_Marker": 0, "Right_Marker": 0, "Select_List": [], "Camera_Mode": "Color_Image", "Graph1_Mode": ["Steering"]}
    if args["--edit_changes"]:
        changes_path = os.path.join(data_folder, "changes.json")
        with open(changes_path) as changes_file:
            client_outputs["Select_List"] = json.load(changes_file)

    Color_Image_folder_path = os.path.join(data_folder , "Color_Image")
    Depth_Image_folder_path = os.path.join(data_folder , "Depth_Image")
    if cfg["SVO_COMPRESSION_MODE"] and not args["--expended_svo"]:
        Color_Image_format = "svo"
        Depth_Image_format = "svo"
    else:
        Color_Image_format = cfg["COLOR_IMAGE_FORMAT"]
        Depth_Image_format = cfg["DEPTH_IMAGE_FORMAT"]

    if Color_Image_format == "svo":
        color_image_loader = Image_Loader(Color_Image_format, svo_path=os.path.join(data_folder, "zed_record.svo"))
    else:
        color_image_loader = Image_Loader(Color_Image_format)
    if Depth_Image_format == "svo":
        depth_image_loader = Image_Loader(Depth_Image_format, os.path.join(data_folder, "zed_record.svo"))
    else:
        depth_image_loader = Image_Loader(Depth_Image_format)

    threading.Thread(target=server_thread, daemon=True, name="Server_Thread").start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()