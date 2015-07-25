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
                                  'landmark process',
                                  predefined_error_metric_path)


def retrieve_error_metric(lm_process_name):
    module = load_module_for_process(lm_process_name)
    return getattr(module, 'error_metric')
