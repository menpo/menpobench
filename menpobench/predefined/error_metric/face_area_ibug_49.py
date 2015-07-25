import numpy as np


def error_metric(gt, final):
    # TODO implement face_area_ibug_49
    return np.sqrt(np.sum((gt.points - final.points) ** 2, axis=-1)).mean()
