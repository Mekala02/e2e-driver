import pyzed.sl as sl

class Camera_IMU:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.outputs = {"IMU_Accel_X": 0, "IMU_Accel_Y": 0, "IMU_Accel_Z": 0, "IMU_Gyro_X": 0, "IMU_Gyro_Y": 0, "IMU_Gyro_Z": 0}
        self.big_outputs = {"RGB": 0, "Depth": 0, "Object_Detection": 0}
        self.RGB_image = 0
        self.depth_image = 0
        self.IMU_Accel_X = 0
        self.IMU_Accel_Y = 0
        self.IMU_Accel_Z = 0
        self.IMU_Gyro_X = 0
        self.IMU_Gyro_Y = 0
        self.IMU_Gyro_Z = 0

        self.zed = sl.Camera()
        self.init_params = sl.InitParameters(
            camera_resolution = sl.RESOLUTION.VGA,
            camera_fps = 100,
            depth_mode=sl.DEPTH_MODE.ULTRA,
            coordinate_units=sl.UNIT.METER,
            coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        )

        if self.zed.open(self.init_params) != sl.ERROR_CODE.SUCCESS:
            print("Error")

        self.runtime_parameters = sl.RuntimeParameters()
        self.zed_RGB = sl.Mat()
        self.zed_depth = sl.Mat()
        self.sensors_data = sl.SensorsData()

    def generate_frames(self):
        err = self.zed.grab(self.runtime_parameters)
        if err == sl.ERROR_CODE.SUCCESS:
            # A new image is available if grab() returns SUCCESS
            self.zed.retrieve_image(self.zed_RGB, sl.VIEW.LEFT)
            self.RGB_image = self.zed_RGB.get_data()

            self.zed.retrieve_image(self.zed_depth, sl.VIEW.DEPTH)
            self.depth_image = self.zed_depth.get_data()

            self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.IMAGE)

            linear_acceleration = self.sensors_data.get_imu_data().get_linear_acceleration()
            self.IMU_Accel_X = linear_acceleration[0]
            self.IMU_Accel_Y = linear_acceleration[1]
            self.IMU_Accel_Z = linear_acceleration[2]

            angular_velocity = self.sensors_data.get_imu_data().get_angular_velocity()
            self.IMU_Gyro_X = angular_velocity[0]
            self.IMU_Gyro_Y = angular_velocity[1]
            self.IMU_Gyro_Z = angular_velocity[2]

        else:
            print(err)

    def start_thread(self):
        while True:
            self.generate_frames()

    def update(self):
        self.memory.memory["IMU_Accel_X"] = self.IMU_Accel_X
        self.memory.memory["IMU_Accel_Y"] = self.IMU_Accel_Y
        self.memory.memory["IMU_Accel_Z"] = self.IMU_Accel_Z

        self.memory.memory["IMU_Gyro_X"] = self.IMU_Gyro_X
        self.memory.memory["IMU_Gyro_Y"] = self.IMU_Gyro_Y
        self.memory.memory["IMU_Gyro_Z"] = self.IMU_Gyro_Z
        
        self.memory.big_memory["RGB"] = self.RGB_image
        self.memory.big_memory["Depth"] = self.depth_image
        self.memory.big_memory["Object_Detection"] = self.RGB_image