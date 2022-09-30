import pyzed.sl as sl
# import cv2

class Camera_IMU:
    def __init__(self):
        self.threaded = True
        self.memory = 0
        self.outputs = {"IMU_Accel_X": 0, "IMU_Accel_Y": 0, "IMU_Accel_Z": 0, "IMU_Gyro_X": 0, "IMU_Gyro_Y": 0, "IMU_Gyro_Z": 0}
        self.big_outputs = {"RGB": 0, "Depth": 0, "Object_Detection": 0}
        # self.camera=cv2.VideoCapture(0)
        self.RGB_image = 0
        self.depth_image = 0

        self.zed = sl.Camera()
        self.init_params = sl.InitParameters(
            camera_resolution = sl.RESOLUTION.VGA,
            camera_fps = 100,
            depth_mode=sl.DEPTH_MODE.ULTRA,
            coordinate_units=sl.UNIT.METER,
            coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        )

        if self.zed.open(self.init_params) != sl.ERROR_CODE.SUCCESS:
            exit(1)

        self.zed_RGB = sl.Mat()
        self.zed_depth = sl.Mat()
        self.runtime_parameters = sl.RuntimeParameters()

    def generate_frames(self):
        err = self.zed.grab(self.runtime_parameters)
        if err == sl.ERROR_CODE.SUCCESS:
            # A new image is available if grab() returns SUCCESS
            self.zed.retrieve_image(self.zed_RGB, sl.VIEW.LEFT)
            self.RGB_image = self.zed_RGB.get_data()

            self.zed.retrieve_image(self.zed_depth, sl.VIEW.DEPTH)
            self.depth_image = self.zed_depth.get_data()

        else:
            print(err)

    def start_thread(self):
        while True:
            self.generate_frames()

    def update(self):
        self.memory.big_memory["RGB"] = self.RGB_image
        self.memory.big_memory["Depth"] = self.depth_image
        self.memory.big_memory["Object_Detection"] = self.RGB_image