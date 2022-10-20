"""
Usage:
    data_cleaner_app.py  <data_dir> [(--c|--copy) <copy_dir>]

Options:
  -h --help     Show this screen.
"""

from flask import Flask, render_template, Response, request, jsonify
from waitress import serve
from docopt import docopt
import numpy as np
import threading
import logging
import json
import time
import cv2
import sys
import os

app=Flask(__name__)
# Servers memory
data = {}

def generate_frames():
    while True:
        # Geeting img id according to our data index (cursor on the bar)
        img_id = datas[client_outputs["Data_Index"]]["Img_Id"]
        # Getting camera mode (RGB, Depth, Object_Detection)
        camera_mode = client_outputs["Camera_Mode"]
        frame_path = os.path.join(data_folder, "big_data", camera_mode)
        image_format = cfg[camera_mode.upper() + "_FORMAT"]
        if image_format == "npy":
            frame = np.load(os.path.join(frame_path, str(img_id) + "." + image_format))
        elif image_format == "npz":
            frame = np.load(os.path.join(frame_path, str(img_id) + "." + image_format))["arr_0"]
        elif image_format == "jpg" or image_format == "jpeg" or image_format == "png":
            frame = cv2.imread(os.path.join(frame_path, str(img_id) + "." + image_format))
        else:
            logger.warning("Unknown Image Format")
        ret, buffer = cv2.imencode('.jpg', frame)
        frame=buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # While loop is too fast we need to slow down interval is 4ms (250fps)
        time.sleep(0.004)

@app.route('/')
def index():
    # Rendering template, and sending necessary data to client side
    return render_template('data_cleaner.html',  outputs={**client_outputs})

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
                search_results.append(row["Img_Id"])
    elif symbol == ">=":
        for row in datas:
            if row[name] >= value:
                search_results.append(row["Img_Id"])
    elif symbol == "<=":
        for row in datas:
            if row[name] <= value:
                search_results.append(row["Img_Id"])
    elif symbol == ">":
        for row in datas:
            if row[name] > value:
                search_results.append(row["Img_Id"])
    elif symbol == "<":
        for row in datas:
            if row[name] < value:
                search_results.append(row["Img_Id"])
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
    send["Img_Id"] = []
    for row in datas:
        # Looping over all dataset and adding neccesry inputs
        send["Img_Id"].append(row["Img_Id"])
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
    # Make it os based this is too slow
    # if args["--c"] or args["--copy"]:
    #     from distutils.dir_util import copy_tree
    #     if args["<copy_dir>"]:
    #         copy_folder = args["<copy_dir>"]
    #     else:
    #         copy_folder = os.path.join(os.path.split(data_folder)[0], folder_name+"_copy")    
    #     os.mkdir(copy_folder)
    #     copy_tree(data_folder, copy_folder)
    #     data_folder = copy_folder
    #     folder_name = os.path.basename(data_folder)
    logger = logging.getLogger(__name__)
    json_path = os.path.join(data_folder, "memory.json")
    cfg_path = os.path.join(data_folder, "cfg.json")
    with open(cfg_path) as cfg_file:
        cfg = json.load(cfg_file)
    datas = json.loads(open(json_path, "r").read())
    # Default values for server startup
    client_outputs = {"Data_Lenght": len(datas), "Data_Index": 0, "Data_Folder": folder_name,
    "Left_Marker": 0, "Right_Marker": 0, "Select_List": [], "Camera_Mode": "RGB_Image", "Graph1_Mode": ["Steering"]}

    threading.Thread(target=server_thread, daemon=True, name="Server_Thread").start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()

# python .\data_cleaner_app.py c:\Users\Mekala\Documents\GitHub\e2e-driver\data\test_data