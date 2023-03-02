import custom_transforms as CustomTransforms
import albumentations as A
from torch.nn import MSELoss
from torch.optim import Adam

from networks import Linear
'''
act_value_type:         if throttle network predict throttle value; elif speed network will predict speed; elif encoder_speed network will predict encoder speed
learning_rate:          2e-3 for startup then reduce to 1e-3
validation_split:       Splits the training data [0,1]
image_resolution:       None or {"height": x, "width": y} if None zed's resolution will be used
reduce_fps:             If set to value like 30 it will make training data ~30fps. It wont work great if datasets fps is close to reduce_fps
other_inputs:           None or list like ["IMU_Accel_X", "IMU_Accel_Y", "IMU_Accel_Z", "IMU_Gyro_X", "IMU_Gyro_Y", "IMU_Gyro_Z", "Speed"]
detailed_tensorboard:   Saves image grid for first train and test set batch
transforms:             Thoose transformations will be applied to all data
train_transforms:       Thoose transformations will be applied only to train set
Delta: Minimum change to qualify as an improvement
Patience:  How many times we wait for change < delta before stop training
'''
Train_Config = dict(
    MODEL = Linear,
    CRITERION = MSELoss,
    OPTIMIZER = Adam,
    # Our input size is not changing so we can use cudnn's optimization
    USE_CUDNN_BENCHMARK = True,
    PATIENCE = 5 ,
    DELTA = 0.000005,
    ACT_VALUE_TYPE = "Speed",
    USE_DEPTH = False,
    LEARNING_RATE = 2e-3,
    BATCH_SIZE = 1024,
    NUM_EPOCHS = 512,
    SHUFFLE_TRAINSET = True,
    VALIDATION_SPLIT = 0.2,
    IMAGE_RESOLUTION = {"height": 120, "width": 160},
    REDUCE_FPS = 10,
    OTHER_INPUTS = None,
    USE_TB = False,
    TB_ADD_GRAPH = False,
    DETAILED_TB = False,
)

TRANSFORMS = dict(
    color_image = [
        ["custom", CustomTransforms.Resize(Train_Config["IMAGE_RESOLUTION"]["width"], Train_Config["IMAGE_RESOLUTION"]["height"])]
    ],
    depth_image = [
        ["custom", CustomTransforms.Resize(Train_Config["IMAGE_RESOLUTION"]["width"], Train_Config["IMAGE_RESOLUTION"]["height"])]
    ]
)
TRAIN_TRANSFORMS = dict(
    color_image = [
        *TRANSFORMS["color_image"],
        ["albumation", 
            A.Compose([
                A.RandomBrightnessContrast(p=0.6, brightness_limit=(-0.30, 0.35), contrast_limit=(-0.2, 0.2), brightness_by_max=True),
                A.RandomGamma(p=0.15, gamma_limit=(80, 120), eps=None),
                A.Blur(p=0.15, blur_limit=(3, 7)),
                A.Sharpen(p=0.1, alpha=(0.2, 0.5), lightness=(0.5, 1.0)),
                A.CLAHE(p=0.03, clip_limit=(2, 5), tile_grid_size=(8, 8)),
                A.Equalize(p=0.05, mode='cv', by_channels=True),
                A.FancyPCA(p=0.05, alpha=0.1),
                A.RandomToneCurve(p=0.1, scale=0.1),
                A.CoarseDropout(p=0.06, max_holes=8, max_height=6, max_width=6, min_holes=4, min_height=6, min_width=6, fill_value=(0, 0, 0), mask_fill_value=None),
                A.RandomRain(p=0.02, slant_lower=-5, slant_upper=5, drop_length=10, drop_width=1, drop_color=(0, 0, 0), blur_value=4, brightness_coefficient=0.7, rain_type='drizzle'),
                A.GaussNoise(p=0.15, var_limit=(10.0, 50.0), per_channel=True, mean=0.0),
            ])
        ],
        ["custom", CustomTransforms.Crop_Without_Remove(p=0.5, crop_top=45)],
        ["custom", CustomTransforms.Crop_Without_Remove(p=0.35, crop_left=30, crop_right=30)]
    ],
    depth_image = [
        *TRANSFORMS["depth_image"]
    ]
)



