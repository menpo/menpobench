from menpobench.utils import load_module
from pathlib import Path
from menpobench import predefined_dataset_path


def load_module_for_dataset(name):
    if name.endswith('.py'):
        print('custom path presented - loading...')
        return load_module(Path(name))
    else:
        print('builtin module used')
        return load_module(predefined_dataset_path(name))


def wrap_dataset_with_preprocessing_step(img_generator):
    from .preprocess import basic_preprocess
    for img in img_generator():
        yield basic_preprocess(img)


def generate_dataset(name):
    module = load_module(predefined_dataset_path(name))
    img_generator = getattr(module, 'generate_dataset')
    return wrap_dataset_with_preprocessing_step(img_generator)
