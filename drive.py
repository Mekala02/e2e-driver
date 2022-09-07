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

while True:
    vehicle.update()
    # vehicle.memory.print_memory()
    time.sleep(0.01)