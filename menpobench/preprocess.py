import numpy as np


def basic_preprocess(img):
    # menpobench does some basic cleanup on all images
    return img.crop_to_landmarks_proportion(0.5)


def menpo_preprocess(img):
    # for menpo methods we always want greyscale. we also don't want images
    # that are too large, and we want floating point images.
    img = img.crop_to_landmarks_proportion(0.2)
    img.pixels = np.array(img.pixels, dtype=np.float) * (1.0 / 255.0)
    if img.n_channels == 3:
        img = img.as_greyscale(mode='luminosity')
    return img
