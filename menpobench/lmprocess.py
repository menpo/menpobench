from functools import partial
from menpobench import predefined_dir
from menpobench.utils import (load_module_with_error_messages,
                              load_callable_with_error_messages)


def predefined_lm_process_dir():
    return predefined_dir() / 'landmark_process'


def predefined_lmprocess_path(name):
    return predefined_lm_process_dir() / '{}.py'.format(name)


def list_predefined_lm_processes():
    return sorted([p.stem for p in predefined_lm_process_dir().glob('*.py')])


load_module_for_process = partial(load_module_with_error_messages,
                                  'landmark process',
                                  predefined_lmprocess_path)


def retrieve_lm_process(name):
    module = load_module_for_process(name)
    return load_callable_with_error_messages(module, 'process', name,
                                             module_type='landmark process')


class CallableChain(object):

    def __init__(self, *callables):
        self.callables = callables

    def __call__(self, x):
        return reduce(lambda y, f: f(y), self.callables, x)


def retrieve_lm_processes(lm_process_def):
    if not isinstance(lm_process_def, list):
        # a single lm_process provided
        return retrieve_lm_process(lm_process_def)
    else:
        # chain together a list of process steps in a row
        return CallableChain(*(retrieve_lm_process(p) for p in lm_process_def))


def apply_lm_process_to_img(lm_process, img):
    img.landmarks['gt'] = lm_process(img.landmarks['gt'].lms)
    return img
