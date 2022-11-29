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
        self.run = True
        self.outputs = {"Color_Image": 0, "Depth_Image": 0, "Object_Detection_Image": 0, "Depth_Array":0, "Zed_Timestamp": 0, "Zed_Data_Id": 0, "IMU_Accel_X": 0, "IMU_Accel_Y": 0, "IMU_Accel_Z": 0, "IMU_Gyro_X": 0, "IMU_Gyro_Y": 0, "IMU_Gyro_Z": 0}
        self.Color_Image = 0
        self.Depth_Image = 0
        self.Depth_Array = 0
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
        if cfg["SVO_COMPRESSION_MODE"]:
            svo_path = os.path.join(memory.untracked["Data_Folder"], "zed_record.svo")
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
        if cfg["SVO_COMPRESSION_MODE"]:
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
            if cfg["CAMERA_RESOLUTION"]:
                Color_Image = cv2.resize(Color_Image, (cfg["CAMERA_RESOLUTION"]), interpolation= cv2.INTER_LINEAR)
            self.Color_Image = Color_Image

            # If we calculating depth
            if not cfg["DEPTH_MODE"] == "NONE":
                # Depth Map As Image
                self.zed.retrieve_image(self.zed_Depth_Image, sl.VIEW.DEPTH)
                Depth_Image = cv2.cvtColor(self.zed_Depth_Image.get_data(), cv2.COLOR_BGRA2BGR)
                if cfg["CAMERA_RESOLUTION"]:
                    Depth_Image = cv2.resize(Depth_Image, (cfg["CAMERA_RESOLUTION"]), interpolation= cv2.INTER_LINEAR)
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
            # Thread is too fast we limiting the run speed othervise other threads will be slow
            # inverse of elapsed time in 1 seond = fps we limiting according to inverse of time, not fps
            sleep_time = 1.0 / cfg["DRIVE_LOOP_HZ"] - (time.time() - start_time)
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def update(self):
        # Recording Zed_Timestamp for synchronizing
        # json saved data and svo saved data
        self.memory.memory["Zed_Timestamp"] = self.Zed_Timestamp
        self.memory.memory["Zed_Data_Id"] = self.Zed_Data_Id
        self.memory.memory["IMU_Accel_X"] = self.IMU_Accel_X
        self.memory.memory["IMU_Accel_Y"] = self.IMU_Accel_Y
        self.memory.memory["IMU_Accel_Z"] = self.IMU_Accel_Z

        self.memory.memory["IMU_Gyro_X"] = self.IMU_Gyro_X
        self.memory.memory["IMU_Gyro_Y"] = self.IMU_Gyro_Y
        self.memory.memory["IMU_Gyro_Z"] = self.IMU_Gyro_Z
        
        self.memory.memory["Color_Image"] = self.Color_Image
        self.memory.memory["Depth_Image"] = self.Depth_Image
        self.memory.memory["Object_Detection_Image"] = 0
        self.memory.memory["Depth_Array"] = self.Depth_Array

        self.record = self.memory.memory["Record"]

    def shut_down(self):
        self.run = False
        # Zed close calls disable_recording so we dont have to explicitly turn of recording
        self.zed.close()
        logger.info("Stopped")