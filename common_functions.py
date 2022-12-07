import logging
logger = logging.getLogger(__name__)

class Image_Loader():
    def __init__(self, img_format, svo_path=None):
        self.img_format = img_format
        if img_format == "jpg" or img_format == "jpeg" or img_format == "png":
            import cv2
            self.f = cv2.imread

        elif img_format == "npy":
            import numpy as np
            self.f = np.load

        elif img_format == "npz":
            import numpy as np
            def load_npz(path):
                return np.load(path)["arr_0"]
            self.f = load_npz

        elif img_format == "svo":
            import pyzed.sl as sl
            import cv2
            import os
            init_parameters = sl.InitParameters()
            init_parameters.set_from_svo_file(svo_path)
            init_parameters.svo_real_time_mode = False
            zed = sl.Camera()
            zed_Color_Image = sl.Mat()
            zed_Depth_Image = sl.Mat()
            zed_Depth_Map = sl.Mat()
            if (err:=zed.open(init_parameters)) != sl.ERROR_CODE.SUCCESS:
                logger.error(err)
            def load_SVO_data(path, zed_data_id, type_):
                # base_name = os.path.basename(path)
                zed.set_svo_position(zed_data_id)
                if (err:=zed.grab()) != sl.ERROR_CODE.SUCCESS:
                    logger.warning(err)
                else:
                    if type_ == "Color_Image":
                        zed.retrieve_image(zed_Color_Image, sl.VIEW.LEFT)
                        color_image = cv2.cvtColor(zed_Color_Image.get_data(), cv2.COLOR_BGRA2BGR)
                        return color_image
                    elif type_ == "Depth_Image":
                        zed.retrieve_image(zed_Depth_Image, sl.VIEW.DEPTH)
                        depth_image = cv2.cvtColor(zed_Depth_Image.get_data(), cv2.COLOR_BGRA2BGR)
                        return depth_image
                    elif type_ == "Depth_Map":
                        zed.retrieve_measure(zed_Depth_Map, sl.MEASURE.DEPTH)
                        depth_array = zed_Depth_Map.get_data()
                        return depth_array
            self.f = load_SVO_data

        else:
            logger.warning("Unsupported Format")
            
    
    def __call__(self, path, zed_data_id=None, type_=None):
        if self.img_format == "svo":
            return self.f(path, zed_data_id, type_)
        return self.f(path)
