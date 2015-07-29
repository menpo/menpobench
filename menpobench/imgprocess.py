import numpy as np
from menpo.shape import PointCloud


def union_bounding_box(landmarks):
    return PointCloud(np.concatenate([landmarks[l].lms.points
                                      for l in landmarks]), copy=False)


def basic_img_process(img):
    # menpobench does some basic cleanup on all images
    img.landmarks['__super_bbox'] = union_bounding_box(img.landmarks)
    new_img = img.crop_to_landmarks_proportion(0.5, group='__super_bbox')
    del new_img.landmarks['__super_bbox']
    del img.landmarks['__super_bbox']
    return img


def menpo_img_process(img, crop=True):
    # for menpo methods we always want greyscale. we also don't want images
    # that are too large, and we want floating point images.
    if crop:
        img.landmarks['__super_bbox'] = union_bounding_box(img.landmarks)
        new_img = img.crop_to_landmarks_proportion(0.2, group='__super_bbox')
        del new_img.landmarks['__super_bbox']
        del img.landmarks['__super_bbox']
    else:
        new_img = img.copy()

    new_img.pixels = np.array(new_img.pixels, dtype=np.float) * (1.0 / 255.0)
    if new_img.n_channels == 3:
        new_img = new_img.as_greyscale(mode='luminosity')
    return new_img
