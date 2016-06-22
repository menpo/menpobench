from functools import reduce

from menpobench import predefined_dir
from menpobench.utils import (load_module_with_error_messages,
                              load_callable_with_error_messages,
                              predefined_module)


def predefined_lm_process_dir():
    return predefined_dir() / 'landmark_process'


def predefined_lmprocess_path(name):
    return predefined_lm_process_dir() / '{}.py'.format(name)


def list_predefined_lm_processes():
    return sorted([p.stem for p in predefined_lm_process_dir().glob('*.py')])


def retrieve_lm_process(name):
    module = load_module_with_error_messages('landmark process',
                                             predefined_lmprocess_path, name)
    process = load_callable_with_error_messages(module, 'process', name,
                                                module_type='landmark process')
    return LandmarkProcess(name, process)


class LandmarkProcess(object):

    def __init__(self, name, process):
        self.name = name
        self.process = process

    def __call__(self, *args, **kwargs):
        return self.process(*args, **kwargs)

    @property
    def predefined(self):
        return predefined_module(self.name)


class LandmarkProcessChain(object):

    def __init__(self, *processes):
        self.processes = processes

    @property
    def predefined(self):
        for p in self.processes:
            if not p.predefined:
                return False
        return True

    @property
    def id(self):
        return tuple(p.name for p in self.processes)

    def __call__(self, x):
        return reduce(lambda y, f: f(y), self.processes, x)


def retrieve_lm_processes(lm_process_def):
    if not isinstance(lm_process_def, list):
        # a single lm_process provided
        lm_process_def = [lm_process_def]
    return LandmarkProcessChain(*(retrieve_lm_process(p) for p in
                                  lm_process_def))


def apply_lm_process_to_img(lm_process, img):
    img.landmarks['gt'] = lm_process(img.landmarks['gt'])
    return img


def id_of_lm_process_or_none(l):
    return l.id if l is not None else tuple()
