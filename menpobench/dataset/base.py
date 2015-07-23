from itertools import chain
from functools import partial
from menpobench import predefined_dir
from menpobench.preprocess import basic_preprocess
from menpobench.utils import load_module_with_error_messages
from menpo.visualize.textutils import print_dynamic


def predefined_dataset_dir():
    return predefined_dir() / 'dataset'


def predefined_dataset_path(name):
    return predefined_dataset_dir() / '{}.py'.format(name)


def list_predefined_datasets():
    return sorted([p.stem for p in predefined_dataset_dir().glob('*.py')])


load_module_for_dataset = partial(load_module_with_error_messages,
                                  'dataset', predefined_dataset_path)


def wrap_dataset_with_preprocessing_step(id_img_iter, preprocess):
    for id_, img in id_img_iter():
        yield id_, preprocess(img)


def retrieve_dataset(dataset_name):
    module = load_module_for_dataset(dataset_name)
    id_and_img_iter = getattr(module, 'generate_dataset')
    # we have a hold on the loading function, but we have some base
    # pre-processing that we always perform per-image. Wrap the generator with
    # the basic pre-processing before we return it.
    return wrap_dataset_with_preprocessing_step(id_and_img_iter,
                                                basic_preprocess)


def print_processing_status(id_img_iter):
    i = 0
    for i, (id_, image) in enumerate(id_img_iter, 1):
        print_dynamic('Processing image {} ({})'.format(i, id_))
        yield id_, image
    print_dynamic('{} images processed.'.format(i))
    print('')


class RetainIds(object):

    def __init__(self, id_img_iter):
        self.id_img_iter = id_img_iter
        self.ids = []

    def __iter__(self):
        return self

    def next(self):
        id_, img = next(self.id_img_iter)
        self.ids.append(id_)
        return img


def swallow_ids(id_img_iter):
    for _, img in id_img_iter:
        yield img


def retrieve_datasets(dataset_names, retain_ids=False):
    # chain together a list of datasets in a row, reporting the progress as
    # we go.
    id_img_iter = print_processing_status(
        chain(*(retrieve_dataset(d) for d in dataset_names)))
    if retain_ids:
        return RetainIds(id_img_iter)
    else:
        return swallow_ids(id_img_iter)
