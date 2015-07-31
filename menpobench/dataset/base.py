from itertools import chain
from functools import partial
from menpobench import predefined_dir
from menpobench.lmprocess import retrieve_lm_processes, apply_lm_process_to_img
from menpobench.imgprocess import basic_img_process
from menpobench.utils import (load_module_with_error_messages,
                              load_callable_with_error_messages, load_schema,
                              memoize)


def predefined_dataset_dir():
    return predefined_dir() / 'dataset'


def predefined_dataset_path(name):
    return predefined_dataset_dir() / '{}.py'.format(name)


def list_predefined_datasets():
    return sorted([p.stem for p in predefined_dataset_dir().glob('*.py')])


@memoize
def dataset_metadata_schema():
    return load_schema(predefined_dir() / 'dataset_metadata_schema.yaml')


def load_and_validate_dataset_module(name):
    # loading a dataset validates the metadata
    module, metadata = load_module_with_error_messages(
        'dataset', predefined_dataset_path, name,
        metadata_schema=dataset_metadata_schema())
    generate_dataset = load_callable_with_error_messages(
        module, 'generate_dataset', name,
        module_type='dataset', generatorfunc=True)
    return generate_dataset, metadata


def wrap_dataset_with_processing(id_img_gen, process):
    for id_, img in id_img_gen:
        yield id_, process(img)


def print_processing_status(id_img_gen):
    from menpo.visualize.textutils import print_dynamic
    i = 0
    for i, (id_, image) in enumerate(id_img_gen, 1):
        print_dynamic('Processing image {} ({})'.format(i, id_))
        yield id_, image
    print_dynamic('{} images processed.'.format(i))
    print('')


# logs ids and gt shapes for later use by menpobench
class TestsetWrapper(object):

    def __init__(self, id_img_gen):
        self.id_img_gen = id_img_gen
        self.ids = []
        self.gt_shapes = []

    def __iter__(self):
        return self

    def next(self):
        id_, img = next(self.id_img_gen)
        self.ids.append(id_)
        self.gt_shapes.append(img.landmarks.pop('gt').lms)
        return img


# discards ids and allows gt shapes through uninterrupted
def trainset_wrapper(id_img_gen):
    for _, img in id_img_gen:
        yield img


# a single dataset. Call provides a generator of (id, image) pairs.
class Dataset(object):

    def __init__(self, dataset_gen_f, name, metadata, lm_process=None):
        self.name = name
        self.metadata = metadata
        self.dataset_gen_f = dataset_gen_f
        self.lm_process = lm_process

    def __call__(self):
        # we have a hold on the loading function, but we have some base
        # pre-processing that we always perform per-image. Wrap the generator
        # with the basic pre-processing
        gen = wrap_dataset_with_processing(self.dataset_gen_f(),
                                           basic_img_process)

        if self.lm_process is not None:
            # the specified lm_processes needs to be added after basic
            # processing
            # -> take the landmark processing and apply it to each image
            img_lm_process = partial(apply_lm_process_to_img, self.lm_process)
            gen = wrap_dataset_with_processing(gen, img_lm_process)

        return gen


# a chain of datasets. self.generator provides a generator of either
# (id, image) or image depending on whether or not test is true or false.
class DatasetChain(object):

    def __init__(self, datasets, test=False):
        self.datasets = datasets
        self.test = test

    def __call__(self):
        # chain together the datasets, and add process reporting
        # notice that we invoke each dataset in turn.
        id_img_gen = print_processing_status(chain(*(d() for d in
                                                     self.datasets)))
        return (TestsetWrapper(id_img_gen) if self.test
                else trainset_wrapper(id_img_gen))

    def __str__(self):
        return ', '.join("'{}'".format(d.name) for d in self.datasets)


def retrieve_dataset(dataset_def):
    lm_process = None
    if isinstance(dataset_def, str):
        name = dataset_def
    else:
        name = dataset_def['name']
        lm_process_def = dataset_def.get('lm_post_load')
        if lm_process_def is not None:
            # user is specifying some landmark processing
            lm_process = retrieve_lm_processes(lm_process_def)

    dataset_gen_f, metadata = load_and_validate_dataset_module(name)
    return Dataset(dataset_gen_f, name, metadata, lm_process=lm_process)


def retrieve_datasets(dataset_defs, test=False):
    return DatasetChain([retrieve_dataset(d) for d in dataset_defs], test=test)
