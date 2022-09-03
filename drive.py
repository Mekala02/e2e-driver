from concurrent.futures import thread
from vehicle import Vehicle
from parts import Memory
from parts.web_server.app import Web_Server
import time

memory = Memory()

vehicle = Vehicle(memory)

web_server = Web_Server(memory)
vehicle.add(web_server)
vehicle.start()

while True:
    vehicle.update()
    memory.print_memory()
    time.sleep(0.5)
    # pass