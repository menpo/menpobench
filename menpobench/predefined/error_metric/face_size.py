import numpy as np
from menpobench.errormetric import mean_error

def error_metric(gt, final):
    # TODO implement face_area_ibug_68
    normalizer = np.mean(np.max(gt.points, axis=0) -
                         np.min(gt.points, axis=0))
    return mean_error(gt, final) / normalizer
