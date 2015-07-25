import numpy as np


def error_metric(gt, final):
    return np.sqrt(np.sum((gt.points - final.points) ** 2, axis=-1)).sum()
