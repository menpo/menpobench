from menpobench.utils import load_module
from pathlib import Path
from menpobench import predefined_dir


def predefined_method_dir():
    return predefined_dir() / 'method'


def predefined_method_path(name):
    return predefined_method_dir() / '{}.py'.format(name)


def predefined_untrainable_method_dir():
    return predefined_dir() / 'untrainable_method'


def predefined_untrainable_method_path(name):
    return predefined_untrainable_method_dir() / '{}.py'.format(name)


def load_module_for_method(name):
    if name.endswith('.py'):
        print('custom path presented - loading...')
        return load_module(Path(name))
    else:
        print('builtin module used')
        return load_module(predefined_method_path(name))


def load_module_for_untrainable_method(name):
    if name.endswith('.py'):
        print('custom path presented - loading...')
        return load_module(Path(name))
    else:
        print('builtin module used')
        return load_module(predefined_untrainable_method_path(name))


def retrieve_method(name):
    module = load_module_for_method(name)
    return getattr(module, 'train')


def retrieve_untrainable_method(name):
    module = load_module_for_method(name)
    return getattr(module, 'test')
