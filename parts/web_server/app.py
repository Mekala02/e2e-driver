from flask import Flask, render_template, Response, request, jsonify, after_this_request
import copy
import cv2

app=Flask(__name__)
camera=cv2.VideoCapture(0)

queue = set()

outputs = {"pilot": "Manuel", "route": "Manuel", "motor_power": 0, "record": 0,
        "speed_factor": 1}

inputs = {"stop": 0, "taxi": 0, "direction": "Forward", "lane": "Right",
        "steering": 0, "throttle": 0, "speed": 0, "IMU": 0, "timestamp": 0}

web_special = {"camera_mode": "RGB", "graph_mode": "Speed/IMU"}

def generate_frames():
    while True:
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            ret, buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
        self.outputs = outputs

    def change_server_memory(self, name, value):
        self.server_memory[name] = value

    def update_vehicle_memory(self):
        # Updates outputs(to vehicle) coming from web server client side
        for key in queue:
            self.memory.memory[key] = outputs[key]
        queue.clear()

    def update_local_memory(self):
        # Updates Inputs(to web server) coming from vehicle
        for key in inputs:
            inputs[key] = self.memory.memory[key]

    def start_thread(self):
        app.run(host='0.0.0.0')
        
    def update(self):
        self.update_vehicle_memory()
        self.update_local_memory()


if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)
