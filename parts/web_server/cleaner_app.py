from flask import Flask, render_template, Response, request, jsonify
import numpy as np
import json
import time
import cv2

app=Flask(__name__)
data_folder = "c:\\Users\\Mekala\\Documents\\GitHub\\e2e-driver\\data"
datas = json.loads(open(f"{data_folder}\\memory.json", "r").read())

client_outputs = {"Data_Position": 0, "Data_Folder": 0, "Camera_Mode": "RGB", "Graph1_Mode": ["Steering"]}

# Servers memory
data = {}

def generate_frames():
    while True:
        img_id = datas[client_outputs["Data_Position"]]["Img_Id"]
        camera_mode = client_outputs["Camera_Mode"]
        frame = np.load(f"{data_folder}\\images\\{camera_mode}\\{img_id}.npy")
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

@app.route('/inputs')
def send_inputs():
    data = datas[client_outputs["Data_Position"]]
    return jsonify(data)

if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)
