import cv2

class Resize:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.interpolation = cv2.INTER_LINEAR
        self.custom = True

    def __call__(self, image):
        return cv2.resize(image, (self.width, self.height), interpolation=self.interpolation)