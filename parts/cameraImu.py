import pyzed.sl as sl
import time
import logging

logger = logging.getLogger(__name__)

class Camera_IMU:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.run = True
        self.outputs = {"IMU_Accel_X": 0, "IMU_Accel_Y": 0, "IMU_Accel_Z": 0, "IMU_Gyro_X": 0, "IMU_Gyro_Y": 0, "IMU_Gyro_Z": 0}
        self.big_outputs = {"RGB_Image": 0, "Depth_Image": 0, "Object_Detection_Image": 0}
        self.RGB_Image = 0
        self.Depth_Image = 0
        self.IMU_Accel_X = 0
        self.IMU_Accel_Y = 0
        self.IMU_Accel_Z = 0
        self.IMU_Gyro_X = 0
        self.IMU_Gyro_Y = 0
        self.IMU_Gyro_Z = 0

        self.zed = sl.Camera()
        self.init_params = sl.InitParameters(
            camera_resolution = sl.RESOLUTION.VGA,
            camera_fps = 90,
            depth_mode=sl.DEPTH_MODE.ULTRA,
            coordinate_units=sl.UNIT.MILLIMETER,
            coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP
        )

        if err:=self.zed.open(self.init_params) != sl.ERROR_CODE.SUCCESS:
            logger.error(err)

        self.runtime_parameters = sl.RuntimeParameters()
        self.zed_RGB_Image = sl.Mat(self.zed.get_camera_information().camera_resolution.width,
            self.zed.get_camera_information().camera_resolution.height,
            sl.MAT_TYPE.U8_C4,
            sl.MEM.CPU)
        self.zed_depth_Image = sl.Mat()
        self.zed_sensors_data = sl.SensorsData()
        self.zed_depth_map = sl.Mat()
        logger.info("Successfully Added")

    def grab_data(self):
        if err:= self.zed.grab(self.runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            # A new image is available if grab() returns SUCCESS
            self.zed.retrieve_image(self.zed_RGB_Image, sl.VIEW.LEFT)
            self.RGB_Image = self.zed_RGB_Image.get_data()

            self.zed.retrieve_image(self.zed_depth_Image, sl.VIEW.DEPTH)
            self.Depth_Image = self.zed_depth_Image.get_data()

            self.zed.retrieve_measure(self.zed_depth_map, sl.MEASURE.DEPTH)
            self.Depth_array = self.zed_depth_map.get_data()

            self.zed.get_sensors_data(self.zed_sensors_data, sl.TIME_REFERENCE.IMAGE)

            imu_data = self.zed_sensors_data.get_imu_data()

            linear_acceleration = imu_data.get_linear_acceleration()
            self.IMU_Accel_X = linear_acceleration[0]
            self.IMU_Accel_Y = linear_acceleration[1]
            self.IMU_Accel_Z = linear_acceleration[2]

            angular_velocity = imu_data.get_angular_velocity()
            self.IMU_Gyro_X = angular_velocity[0]
            self.IMU_Gyro_Y = angular_velocity[1]
            self.IMU_Gyro_Z = angular_velocity[2]
        else:
            logger.error(err)
        # Giving time for other threads
        # Limiting the max loop count to 500 per second
        time.sleep(0.002)

    def start_thread(self):
        logger.info("Starting Thread")
        while self.run:
            self.grab_data()

    def update(self):
        self.memory.memory["IMU_Accel_X"] = self.IMU_Accel_X
        self.memory.memory["IMU_Accel_Y"] = self.IMU_Accel_Y
        self.memory.memory["IMU_Accel_Z"] = self.IMU_Accel_Z

        self.memory.memory["IMU_Gyro_X"] = self.IMU_Gyro_X
        self.memory.memory["IMU_Gyro_Y"] = self.IMU_Gyro_Y
        self.memory.memory["IMU_Gyro_Z"] = self.IMU_Gyro_Z
        
        self.memory.big_memory["RGB_Image"] = self.RGB_Image
        self.memory.big_memory["Depth_Image"] = self.Depth_Image
        self.memory.big_memory["Object_Detection_Image"] = 0

        self.memory.big_memory["Depth_Array"] = self.Depth_array

    def shut_down(self):
        self.run = False
        self.zed.close()
        logger.info("Stopped")