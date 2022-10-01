from flask import Flask, render_template, Response, request, jsonify
from waitress import serve
import time
import cv2

app=Flask(__name__)

queue = set()

# Default values
outputs = {"Pilot_Mode": "Manuel", "Route_Mode": "Manuel", "Motor_Power": 0, "Record": 0,
        "Speed_Factor": 1}

# Servers memory
inputs = {}

# It contains latest image like rgb, depth, yolo and new is for
# tracking if there is new image on it
camera = {"Is_New": False}

web_special = {"Camera_Mode": "RGB", "Graph1_Mode": ["Steering"], "Graph2_Mode": ["Throttle"]}

def generate_frames():
    while True:
        if camera["Is_New"]:
            frame = camera[web_special["Camera_Mode"]]
            ret, buffer = cv2.imencode('.jpg', frame)
            frame=buffer.tobytes()
            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            camera["Is_New"] = False
        # While loop is too fast we need to slow down interval is 2ms (500fps)
        time.sleep(0.002)

@app.route('/')
def index():
    return render_template('main.html', outputs={**outputs, **web_special})

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/outputs', methods=['GET', 'POST'])
def receive_outputs():
    information = request.get_json()
    for key in information.keys():
        if key in web_special:
            web_special[key] = information[key]
        else:
            outputs[key] = information[key]
            queue.add(key)
    return information

@app.route('/inputs')
def send_inputs():
    return jsonify(inputs)

# Wrapper Class flask app problematic when inside the class
class Web_Server:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.run = True
        self.outputs = outputs

    def update_vehicle_memory(self):
        # Updates outputs(to vehicle) coming from web server client side
        for key in queue:
            self.memory.memory[key] = outputs[key]
        queue.clear()

    def update_local_memory(self):
        # Updates Inputs(to web server) coming from vehicle
        for key in self.memory.memory:
            inputs[key] = self.memory.memory[key]
        for key in self.memory.big_memory:
            camera[key] = self.memory.big_memory[key]
        camera["Is_New"] = True

    def start_thread(self):
        serve(app, host="0.0.0.0", port=8080)
        
    def update(self):
        self.update_vehicle_memory()
        self.update_local_memory()

    def shut_down(self):
        self.run = False


if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)
