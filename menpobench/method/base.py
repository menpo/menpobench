from menpobench.utils import load_module
from pathlib import Path
from menpobench import predefined_method_path


def load_module_for_method(name):
    if name.endswith('.py'):
        print('custom path presented - loading...')
        return load_module(Path(name))
    else:
        print('builtin module used')
        return load_module(predefined_method_path(name))


def train(name):
    module = load_module_for_method(name)
    return getattr(module, 'train')
