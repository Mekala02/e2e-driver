from flask import Flask, render_template, Response, request, jsonify
from waitress import serve
import logging
import time
import cv2

logger = logging.getLogger(__name__)
app=Flask(__name__)

queue = set()

# Default values
outputs = {"Pilot_Mode": "Manuel", "Route_Mode": "Manuel", "Motor_Power": 0, "Record": 0,
        "Speed_Factor": 1}

# Servers memory
inputs = {}

# It contains latest image like color, depth, yolo and new is for
# tracking if there is new image on it
camera = {"Is_New": False}

web_special = {"Camera_Mode": "Color_Image", "Graph1_Mode": ["Steering"], "Graph2_Mode": ["Throttle"]}

image_refresh_rate = 30
def generate_frames():
    while True:
        start_time = time.time()
        if camera["Is_New"]:
            frame = camera["frame"]
            ret, buffer = cv2.imencode('.jpg', frame)
            frame=buffer.tobytes()
            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            camera["Is_New"] = False
        # While loop is too fast we need to slow down
        sleep_time = 1.0 / image_refresh_rate - (time.time() - start_time)
        if sleep_time > 0.0:
            time.sleep(sleep_time)

@app.route('/')
def index():
    return render_template('drive_main.html', outputs={**outputs, **web_special})

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
    def __init__(self, memory):
        self.memory = memory
        self.thread = "Single"
        self.run = True
        self.outputs = outputs
        logger.info("Successfully Added")

    def update_vehicle_memory(self):
        # Updates outputs(to vehicle) coming from web server client side
        for key in queue:
            self.memory.memory[key] = outputs[key]
        queue.clear()

    def update_local_memory(self):
        # Updates Inputs(to web server) coming from vehicle
        inputs["overwrite"] = {}
        for key in self.memory.memory:
            inputs[key] = self.memory.memory[key]
        for key in self.memory.overwrite.copy():
            # If we have overwrites, sending adding them to dict o send web server jss
            if key in self.outputs:
                inputs["overwrite"][key] = self.memory.overwrite.pop(key)["value"]
        camera["frame"] = self.memory.big_memory[web_special["Camera_Mode"]]
        camera["Is_New"] = True

    def start_thread(self):
        logger.info("Starting Thread")
        serve(app, host="0.0.0.0", port=8080, threads=6)
        
    def update(self):
        self.update_vehicle_memory()
        self.update_local_memory()

    def shut_down(self):
        self.run = False
        logger.info("Stopped")


if __name__=="__main__":
    app.run(host='0.0.0.0', debug=True)
