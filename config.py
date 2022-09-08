Config = dict(
    DRIVE_LOOP_HZ = 50,
    # if ACT_VALUE_TYPE == Throttle; network directly predict throttle value
    # elif ACT_VALUE_TYPE == Speed; network will predict speed
    # Throttle or Speed    
    ACT_VALUE_TYPE = "Throttle",
    TRANSMITTER_STICK_SPEED_MULTIPLIER = 2.5,
    K_PID = {"Kp":0.2, "Ki":0.4, "Kd":0.001, "I_max":0.35},
    
    USE_OBJECT_DETECTION = False,
    USE_DAGGER = True,
    # If REDUCED_CAMERA_RESOLUTION == None ZED_RESOLUTION will be used
    # None or {"WIDTH": x, "HEIGHT": y}
    REDUCED_CAMERA_RESOLUTION = {"HEIGHT": 120, "WIDTH": 160},

    ZED_RESOLUTION = "VGA",
    CAMERA_FPS = 50,
    CAMERA_IMAGE_FLIP = "OFF",
    # NONE, PERFORMANCE, QUALITY, ULTRA
    DEPTH_MODE = "PERFORMANCE",
    COORDINATE_UNITS = "CENTIMETER",
    COORDINATE_SYSTEM = "RIGHT_HANDED_Z_UP",

    # RGB, RGBD, D
    NETWORK_INPUT_TYPE = "RGBD"
    # If SVO_COMPRESSION_MODE != None other formats won't be used
    # None H264, H264_LOSSLESS
    SVO_COMPRESSION_MODE = "H264",
    # jpg, jpeg, png, npy, npz
    COLOR_IMAGE_FORMAT = "jpg",
    DEPTH_IMAGE_FORMAT = "jpg",
    OBJECT_DETECTION_FORMAT = "npy",


    STEERING_MIN = -0.45,
    STEERING_MAX = 0.45,
    THROTTLE_MIN = -0.4,
    THROTTLE_MAX = 0.4,
    STEERING_OFFSET = 0.53,
    

    # Copilot
    # Thresholds for turning off turn signals (pwm)
    CANCEL_TURN_SIGNAL = True,
    LEFT_THRESHOLD = 1850,
    RIGHT_THRESHOLD = 1260
)
