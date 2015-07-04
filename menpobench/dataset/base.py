from menpobench.utils import load_module_with_error_messages
from menpobench import predefined_dir
from itertools import chain
from functools import partial


def predefined_dataset_dir():
    return predefined_dir() / 'dataset'


def predefined_dataset_path(name):
    return predefined_dataset_dir() / '{}.py'.format(name)


load_module_for_dataset = partial(load_module_with_error_messages,
                                  'dataset', predefined_dataset_path)


def wrap_dataset_with_preprocessing_step(img_generator):
    from .preprocess import basic_preprocess
    for img in img_generator():
        yield basic_preprocess(img)


def retrieve_dataset(dataset_name):
    module = load_module_for_dataset(dataset_name)
    img_generator = getattr(module, 'generate_dataset')
    # we have a hold on the loading function, but we have some base
    # preprocessing that we always perform per-image. Wrap the generator with
    # the basic preprocessing before we return it.
    return wrap_dataset_with_preprocessing_step(img_generator)


def retrieve_datasets(dataset_names):
    # chain together a list of datasets in a row
    return chain(*(retrieve_dataset(d) for d in dataset_names))
