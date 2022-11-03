config = dict(
    USE_OBJECT_DETECTION = True,
    USE_COPILOT = True,

    # If SVO_COMPRESSION_MODE != None other formats will be overwritten
    SVO_COMPRESSION_MODE = "H264",
    RGB_IMAGE_FORMAT = "jpg",
    DEPTH_IMAGE_FORMAT = "npz",
    OBJECT_DETECTION_FORMAT = "npy",

    CAMERA_RESOLUTION = "VGA",
    CAMERA_FPS = 100,
    CAMERA_IMAGE_FLIP = "ON",
    DEPTH_MODE = "ULTRA",
    COORDINATE_UNITS = "CENTIMETER",
    COORDINATE_SYSTEM = "RIGHT_HANDED_Z_UP",

    THROTTLE_FORWARD_PWM = 500,
    THROTTLE_STOPPED_PWM = 370,
    THROTTLE_REVERSE_PWM = 220,
    # Full right
    STEERING_MIN_PWM = 1200,
    STEERING_MID_PWM = 1540,
    # Ful left
    STEERING_MAX_PWM = 1900,
    ENCODER_UNITS = "cm/s",
    ENCODER_TICKS = 600,
    DRIVE_LOOP_HZ = 150,
    TICKS_PER_CM = 11.7
)
