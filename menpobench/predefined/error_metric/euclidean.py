from menpobench.errormetric import mean_error


def error_metric(gt, final):
    return mean_error(gt, final)
