import numpy as np
import cv2

class Resize:
    def __init__(self, width, height):
        '''
        Resizes the image
        '''
        self.width = width
        self.height = height
        self.interpolation = cv2.INTER_LINEAR
        self.custom = True

    def __call__(self, image):
        return cv2.resize(image, (self.width, self.height), interpolation=self.interpolation)

class Crop_Without_Remove:
    '''
    Crops the image but not deletes the pixels intead overwrites them to 0
    Upper left is (0,0)
    '''
    def __init__(self, crop_top=0, crop_bottom=0, crop_left=0, crop_right=0):
        self.crop_top = crop_top
        self.crop_bottom = crop_bottom
        self.crop_left = crop_left
        self.crop_right = crop_right

    def __call__(self, image):
        height, width, channel = image.shape
        multiplier = np.zeros(image.shape, dtype=np.float32)
        multiplier[self.crop_top:height-self.crop_bottom, self.crop_left:width-self.crop_right, :] = 1
        return np.multiply(image, multiplier)
    