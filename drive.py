"""
Usage:
    drive.py  [<data_dir>]

Options:
  -h --help     Show this screen.
"""

from config import config as cfg
from vehicle import Vehicle
from parts.memory import Memory
from parts.cameraImu import Camera_IMU
from parts.object_detection.yolo import Yolo
from parts.copilot.copilot import Copilot
from parts.pilot.pilot import Pilot
from parts.arduino.arduino import Arduino
from parts.data_logger import Data_Logger
from parts.web_server.drive_server import Web_Server
from parts.fps_counter import FPS_Counter

from docopt import docopt
import logging
import sys
import time


args = docopt(__doc__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: @ %(name)s %(message)s")
logger = logging.getLogger("drive")

vehicle_memory = Memory()
vehicle = Vehicle(vehicle_memory)

model_folder_path = args["<data_dir>"]
if model_folder_path:
    vehicle_memory.untracked["Model_Folder_Path"] = model_folder_path

logger.info("Adding parts to vehicle ... \n")
vehicle.add(Data_Logger(vehicle_memory))
vehicle.add(Camera_IMU(vehicle_memory))
if cfg["USE_OBJECT_DETECTION"]:
    vehicle.add(Yolo(vehicle_memory))
if cfg["USE_COPILOT"]:
    vehicle.add(Copilot(vehicle_memory))
vehicle.add(Pilot(vehicle_memory))
vehicle.add(Arduino(vehicle_memory))
vehicle.add(Web_Server(vehicle_memory))
vehicle.add(FPS_Counter(vehicle_memory))

vehicle.start()

logger.info("Starting the drive loop \n")
rate_hz = cfg["DRIVE_LOOP_HZ"]
try:
    while True:
        start_time = time.time()
        vehicle.update()
        sleep_time = 1.0 / rate_hz - (time.time() - start_time)
        if sleep_time > 0.0:
            time.sleep(sleep_time)
except KeyboardInterrupt:
    vehicle.shut_down()
    logger.info("Vehicle Shut Down \n")
    sys.exit()