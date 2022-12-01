from config import config as cfg

import pyzed.sl as sl
import time
import logging
import os
import cv2

logger = logging.getLogger(__name__)


class Camera_IMU:
    def __init__(self, memory=0):
        self.memory = memory
        self.thread = "Single"
        self.thread_hz = cfg["DRIVE_LOOP_HZ"]
        self.run = True
        self.use_depth = cfg["DEPTH_MODE"]
        self.svo_mode = True if cfg["SVO_COMPRESSION_MODE"] else False
        self.reduced_camera_resolution = cfg["REDUCED_CAMERA_RESOLUTION"]
        self.outputs = {"Color_Image": 0, "Zed_Timestamp": 0, "Zed_Data_Id": 0,
            "IMU_Accel_X": 0, "IMU_Accel_Y": 0, "IMU_Accel_Z": 0, "IMU_Gyro_X": 0, "IMU_Gyro_Y": 0, "IMU_Gyro_Z": 0}
        if self.use_depth:
            self.outputs["Depth_Image"] = 0
            self.outputs["Depth_Array"] = 0
            self.Depth_Image = 0
            self.Depth_Array = 0
        self.Color_Image = 0
        self.Zed_Timestamp = 0
        self.Zed_Data_Id = 0
        self.IMU_Accel_X = 0
        self.IMU_Accel_Y = 0
        self.IMU_Accel_Z = 0
        self.IMU_Gyro_X = 0
        self.IMU_Gyro_Y = 0
        self.IMU_Gyro_Z = 0
        self.record = 0

        self.zed = sl.Camera()
        self.init_params = sl.InitParameters(
            camera_resolution=getattr(sl.RESOLUTION, cfg["ZED_RESOLUTION"]),
            camera_fps=cfg["CAMERA_FPS"],
            camera_image_flip=getattr(sl.FLIP_MODE, cfg["CAMERA_IMAGE_FLIP"]),
            depth_mode=getattr(sl.DEPTH_MODE, cfg["DEPTH_MODE"]),
            coordinate_units=getattr(sl.UNIT, cfg["COORDINATE_UNITS"]),
            coordinate_system=getattr(sl.COORDINATE_SYSTEM, cfg["COORDINATE_SYSTEM"])
        )
        if (err:=self.zed.open(self.init_params)) != sl.ERROR_CODE.SUCCESS:
            logger.error(err)
        # If we save data in svo format we opening svo file and activating recording
        if self.svo_mode:
            svo_path = os.path.join(self.memory.memory["Data_Folder"], "zed_record.svo")
            recording_param = sl.RecordingParameters(svo_path, getattr(sl.SVO_COMPRESSION_MODE, cfg["SVO_COMPRESSION_MODE"]))
            if ((err:=self.zed.enable_recording(recording_param)) == sl.ERROR_CODE.SUCCESS):
                self.zed.pause_recording(True)
            else:
                logger.error(repr(err))
        self.runtime_parameters = sl.RuntimeParameters()
        camera_information = self.zed.get_camera_information()
        self.zed_Color_Image = sl.Mat(camera_information.camera_resolution.width, camera_information.camera_resolution.height, sl.MAT_TYPE.U8_C4)
        self.zed_Depth_Image = sl.Mat(camera_information.camera_resolution.width, camera_information.camera_resolution.height, sl.MAT_TYPE.U8_C4)
        self.zed_sensors_data = sl.SensorsData()
        self.zed_depth_map = sl.Mat()
        logger.info("Successfully Added")

    def grab_data(self):
        if self.svo_mode:
            if self.record:
                self.zed.pause_recording(False)
            else:
                self.zed.pause_recording(True)
        if (err:=self.zed.grab(self.runtime_parameters)) == sl.ERROR_CODE.SUCCESS:
            if self.record and self.zed.get_recording_status().status:
                self.Zed_Data_Id += 1

            self.Zed_Timestamp = self.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()
            self.zed.retrieve_image(self.zed_Color_Image, sl.VIEW.LEFT)
            Color_Image = cv2.cvtColor(self.zed_Color_Image.get_data(), cv2.COLOR_BGRA2BGR)
            if self.reduced_camera_resolution:
                Color_Image = cv2.resize(Color_Image, (self.reduced_camera_resolution["WIDTH"], self.reduced_camera_resolution["HEIGHT"]), interpolation= cv2.INTER_LINEAR)
            self.Color_Image = Color_Image

            # If we calculating depth
            if self.use_depth:
                # Depth Map As Image
                self.zed.retrieve_image(self.zed_Depth_Image, sl.VIEW.DEPTH)
                Depth_Image = cv2.cvtColor(self.zed_Depth_Image.get_data(), cv2.COLOR_BGRA2BGR)
                if self.reduced_camera_resolution:
                    Depth_Image = cv2.resize(Depth_Image, (self.reduced_camera_resolution["WIDTH"], self.reduced_camera_resolution["HEIGHT"]), interpolation= cv2.INTER_LINEAR)
                self.Depth_Image = Depth_Image
                self.zed.retrieve_measure(self.zed_depth_map, sl.MEASURE.DEPTH)
                self.Depth_Array = self.zed_depth_map.get_data()

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

    def start_thread(self):
        logger.info("Starting Thread")
        while self.run:
            start_time = time.time()
            self.grab_data()
            sleep_time = 1.0 / self.thread_hz - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        # Recording Zed_Timestamp for synchronizing json and svo saved
        self.memory.memory["Zed_Timestamp"] = self.Zed_Timestamp
        self.memory.memory["Zed_Data_Id"] = self.Zed_Data_Id

        self.memory.memory["IMU_Accel_X"] = self.IMU_Accel_X
        self.memory.memory["IMU_Accel_Y"] = self.IMU_Accel_Y
        self.memory.memory["IMU_Accel_Z"] = self.IMU_Accel_Z
        self.memory.memory["IMU_Gyro_X"] = self.IMU_Gyro_X
        self.memory.memory["IMU_Gyro_Y"] = self.IMU_Gyro_Y
        self.memory.memory["IMU_Gyro_Z"] = self.IMU_Gyro_Z
        
        self.memory.memory["Color_Image"] = self.Color_Image

        if self.use_depth:
            self.memory.memory["Depth_Image"] = self.Depth_Image
            self.memory.memory["Depth_Array"] = self.Depth_Array

        self.record = self.memory.memory["Record"]

    def shut_down(self):
        self.run = False
        # Zed close calls disable_recording so we don't have to explicitly turn of recording
        self.zed.close()
        logger.info("Stopped")