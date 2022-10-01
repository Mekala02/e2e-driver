from vehicle import Vehicle
from parts.memory import Memory
from parts.cameraImu import Camera_IMU
from parts.object_detection.yolo import Yolo
from parts.copilot.copilot import Copilot
from parts.pilot.pilot import Pilot
from parts.arduino import Arduino
from parts.data_logger import Data_Logger
from parts.web_server.app import Web_Server
from parts.fps_counter import FPS_Counter
import sys
import time

vehicle = Vehicle()

vehicle.memory = Memory()

vehicle.add(Camera_IMU())
vehicle.add(Yolo())
vehicle.add(Copilot())
vehicle.add(Pilot())
vehicle.add(Arduino())
vehicle.add(Data_Logger())
vehicle.add(Web_Server())
vehicle.add(FPS_Counter())

vehicle.start()


rate_hz = 20000
try:
    while True:
        start_time = time.time()
        vehicle.update()
        sleep_time = 1.0 / rate_hz - (time.time() - start_time)
        if sleep_time > 0.0:
            time.sleep(sleep_time)
        # vehicle.memory.print_memory()
except KeyboardInterrupt:
    vehicle.shut_down()
    print("Stopped")
    sys.exit()