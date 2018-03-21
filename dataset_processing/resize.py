import cv2


def is_landscape(image):
    dimensions = image.shape
    return dimensions[0] > dimensions[1]


def resize(image):
    if is_landscape(image):
        return cv2.resize(image, (156, 208))
    else:
        return cv2.resize(image, (208, 156))
