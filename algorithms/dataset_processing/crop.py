def crop_scale(image):
    return image[:, 127:]


def crop_seek_logo(image):
    return image[:-74, :]


def crop_location(image):
    return image[168:, :]
