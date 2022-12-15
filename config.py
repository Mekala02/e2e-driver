config = dict(
    DRIVE_LOOP_HZ = 50,
    # if ACT_VALUE_TYPE == Throttle; network directly predict throttle value
    # elif ACT_VALUE_TYPE == Speed; network will predict speed
    # Throttle or Speed    
    ACT_VALUE_TYPE = "Speed",
    TRANSMITTER_STICK_SPEED_MULTIPLIER = 2.5,
    K_PID = {"Kp":0.2, "Ki":0.4, "Kd":0.001, "I_max":0.35},
    
    USE_OBJECT_DETECTION = False,
    USE_DAGGER = True,
    # If REDUCED_CAMERA_RESOLUTION == None ZED_RESOLUTION will be used
    # None or {"WIDTH": x, "HEIGHT": y}
    REDUCED_CAMERA_RESOLUTION = {"HEIGHT": 120, "WIDTH": 160},

    ZED_RESOLUTION = "VGA",
    CAMERA_FPS = 50,
    CAMERA_IMAGE_FLIP = "ON",
    # NONE, PERFORMANCE, QUALITY, ULTRA
    DEPTH_MODE = "NONE",
    COORDINATE_UNITS = "CENTIMETER",
    COORDINATE_SYSTEM = "RIGHT_HANDED_Z_UP",

    # If SVO_COMPRESSION_MODE != None other formats won't be used
    # None H264, H264_LOSSLESS
    SVO_COMPRESSION_MODE = "H264",
    # jpg, jpeg, png, npy, npz
    COLOR_IMAGE_FORMAT = "jpg",
    DEPTH_IMAGE_FORMAT = "jpg",
    OBJECT_DETECTION_FORMAT = "npy",

    THROTTLE_MIN_PWM = 1350,
    THROTTLE_MID_PWM = 1500,
    THROTTLE_MAX_PWM = 1800,
    # Full right
    STEERING_MIN_PWM = 1200,
    STEERING_MID_PWM = 1540,
    # Ful left
    STEERING_MAX_PWM = 1900,
    ENCODER_UNITS = "m/s",
    ENCODER_TICKS_PER_UNIT = 11.7 * 10**2,

    # Copilot
    # Thresholds for turning off turn signals (pwm)
    CANCEL_TURN_SIGNAL = True,
    LEFT_THRESHOLD = 1850,
    RIGHT_THRESHOLD = 1260
)
