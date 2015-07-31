import numpy as np
from menpobench import predefined_dir
from menpobench.utils import (load_module_with_error_messages,
                              load_callable_with_error_messages)


def predefined_error_metric_dir():
    return predefined_dir() / 'error_metric'


def predefined_error_metric_path(name):
    return predefined_error_metric_dir() / '{}.py'.format(name)


def list_predefined_error_metrics():
    return sorted([p.stem for p in predefined_error_metric_dir().glob('*.py')])


def retrieve_error_metric(name):
    module = load_module_with_error_messages('error metric',
                                             predefined_error_metric_path,
                                             name)
    metric = load_callable_with_error_messages(module, 'error_metric', name,
                                               module_type='error metric')
    return name, metric


def retrieve_error_metrics(error_metrics_def):
    if not isinstance(error_metrics_def, list):
        error_metrics_def = [error_metrics_def]
    return [retrieve_error_metric(n) for n in error_metrics_def]


def mean_error(gt, final):
    return np.mean(np.sqrt(np.sum((gt - final) ** 2, axis=-1)))


def root_mean_squared_error(target, gt_shape):
    return np.sqrt(np.mean((target.flatten() - gt_shape.flatten()) ** 2))
