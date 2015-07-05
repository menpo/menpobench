from menpobench.utils import load_module_with_error_messages
from menpobench import predefined_dir
from functools import partial


class MenpoFitterWrapper(object):

    def __init__(self, fitter):
        self.fitter = fitter

    def __call__(self, img):
        return self.fitter.fit(img)


def predefined_method_dir():
    return predefined_dir() / 'method'


def predefined_untrainable_method_dir():
    return predefined_dir() / 'untrainable_method'


def predefined_method_path(name):
    return predefined_method_dir() / '{}.py'.format(name)


def predefined_untrainable_method_path(name):
    return predefined_untrainable_method_dir() / '{}.py'.format(name)


load_module_for_method = partial(load_module_with_error_messages,
                                 'method', predefined_method_path)

load_module_for_untrainable_method = partial(
    load_module_with_error_messages, 'untrainable method',
    predefined_untrainable_method_path)


def retrieve_method(name):
    module = load_module_for_method(name)
    return getattr(module, 'train')


def retrieve_untrainable_method(name):
    module = load_module_for_untrainable_method(name)
    return getattr(module, 'test')
