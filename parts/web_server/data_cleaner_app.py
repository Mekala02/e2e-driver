"""
Usage:
    data_cleaner_app.py  <data_dir> [(--c|--copy) <copy_dir>]

Options:
  -h --help     Show this screen.
"""

from docopt import docopt
from flask import Flask, render_template, Response, request, jsonify
import numpy as np
import os
import json
import time
import cv2

app=Flask(__name__)

# Servers memory
data = {}

def generate_frames():
    while True:
        img_id = datas[client_outputs["Data_Index"]]["Img_Id"]
        camera_mode = client_outputs["Camera_Mode"]
        frame_path = os.path.join(data_folder, "images", camera_mode, f"{img_id}.npy")
        frame = np.load(frame_path)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame=buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # While loop is too fast we need to slow down interval is 4ms (250fps)
        time.sleep(0.004)

@app.route('/')
def index():
    return render_template('data_cleaner.html',  outputs={**client_outputs})

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/outputs', methods=['GET', 'POST'])
def receive_outputs():
    information = request.get_json()
    for key in information.keys():
        client_outputs[key] = information[key]
    return information

search_results = []
@app.route('/search', methods=['GET', 'POST'])
def receive_search():
    search_phrase = request.get_json()
    search_phrase = search_phrase.replace(" ", "")
    search_results.clear()
    delimiters = ["==", ">=", "<=", ">", "<"]
    for delimiter in delimiters:
        try:
            name, value = search_phrase.split(delimiter)
            name = name.capitalize()
            value = value.capitalize()
            print(name, value)
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
def send_search_results():
    return jsonify(search_results)

@app.route('/inputs')
def send_inputs():
    data = datas[client_outputs["Data_Index"]]
    return jsonify(data)

@app.route('/graph')
def send_graph():
    send = {}
    for mode in client_outputs["Graph1_Mode"]:
        send[mode] = []
    send["Img_Id"] = []
    for row in datas:
        send["Img_Id"].append(row["Img_Id"])
        for mode in client_outputs["Graph1_Mode"]:
            send[mode].append(row[mode])
    return jsonify(send)

if __name__=="__main__":
    args = docopt(__doc__)
    data_folder = args["<data_dir>"]
    folder_name = os.path.basename(data_folder)
    json_path = os.path.join(data_folder, "memory.json")
    datas = json.loads(open(json_path, "r").read())
    client_outputs = {"Data_Lenght": len(datas), "Data_Index": 0, "Data_Folder": folder_name,
    "Left_Marker": 500, "Right_Marker": 1000, "Select_List": [], "Camera_Mode": "RGB", "Graph1_Mode": ["Steering"]}
    app.run(host='0.0.0.0', debug=True)

# python .\data_cleaner_app.py c:\Users\Mekala\Documents\GitHub\e2e-driver\data\test_data