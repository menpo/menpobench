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
    # pre-processing that we always perform per-image. Wrap the generator with
    # the basic pre-processing before we return it.
    return wrap_dataset_with_preprocessing_step(img_generator)


from menpo.visualize.textutils import print_dynamic


def print_processing_status(image_generator):
    i = 0
    for i, image in enumerate(image_generator, 1):
        print_dynamic('Pre-processing image {}'.format(i))
        yield image
    print_dynamic('{} images pre-processed.'.format(i))
    print('')


def retrieve_datasets(dataset_names):
    # chain together a list of datasets in a row, reporting the progress as
    # we go.
    return print_processing_status(
        chain(*(retrieve_dataset(d) for d in dataset_names)))
