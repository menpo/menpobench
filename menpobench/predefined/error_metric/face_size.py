import numpy as np
from menpobench.errormetric import mean_error


def error_metric(gt, final):
    normalizer = np.mean(np.max(gt, axis=0) - np.min(gt, axis=0))
    return mean_error(gt, final) / normalizer
