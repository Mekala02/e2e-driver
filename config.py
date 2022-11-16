config = dict(
    DRIVE_LOOP_HZ = 120,
    USE_OBJECT_DETECTION = False,
    USE_DAGGER = True,
    # None or (Width, High), if None Zed resolutio will be used
    CAMERA_RESOLUTION = (160, 120),

    ZED_RESOLUTION = "VGA",
    CAMERA_FPS = 100,
    CAMERA_IMAGE_FLIP = "ON",
    # NONE, PERFORMANCE, QUALITY, ULTRA
    DEPTH_MODE = "NONE",
    COORDINATE_UNITS = "CENTIMETER",
    COORDINATE_SYSTEM = "RIGHT_HANDED_Z_UP",

    # If SVO_COMPRESSION_MODE != None other formats will be overwritten
    # H264, H264_LOSSLESS
    SVO_COMPRESSION_MODE = "H264",
    # jpg, jpeg, png, npy, npz
    RGB_IMAGE_FORMAT = "jpg",
    DEPTH_IMAGE_FORMAT = "jpg",
    OBJECT_DETECTION_FORMAT = "npy",

    THROTTLE_FORWARD_PWM = 2000,
    THROTTLE_STOPPED_PWM = 1500,
    THROTTLE_REVERSE_PWM = 1000,
    # Full right
    STEERING_MIN_PWM = 1200,
    STEERING_MID_PWM = 1540,
    # Ful left
    STEERING_MAX_PWM = 1900,
    ENCODER_UNITS = "cm/s",
    ENCODER_TICKS = 600,
    TICKS_PER_CM = 11.7
)
