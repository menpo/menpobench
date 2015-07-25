from functools import partial
from menpobench import predefined_dir
from menpobench.utils import load_module_with_error_messages


def predefined_error_metric_dir():
    return predefined_dir() / 'error_metric'


def predefined_error_metric_path(name):
    return predefined_error_metric_dir() / '{}.py'.format(name)


def list_predefined_error_metrics():
    return sorted([p.stem for p in predefined_error_metric_dir().glob('*.py')])


load_module_for_process = partial(load_module_with_error_messages,
                                  'error metric',
                                  predefined_error_metric_path)


def retrieve_error_metric(error_metric_name):
    module = load_module_for_process(error_metric_name)
    return error_metric_name, getattr(module, 'error_metric')


def retrieve_error_metrics(error_metrics_def):
    if not isinstance(error_metrics_def, list):
        error_metrics_def = [error_metrics_def]
    return [retrieve_error_metric(n) for n in error_metrics_def]
