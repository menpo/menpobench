from itertools import chain
from functools import partial

from menpobench import predefined_dir
from menpobench.lmprocess import retrieve_lm_processes, apply_lm_process_to_img
from menpobench.imgprocess import basic_img_process
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


def wrap_dataset_with_processing(id_img_gen, process):
    for id_, img in id_img_gen:
        yield id_, process(img)


def retrieve_dataset(dataset_def):
    lm_process = None
    if isinstance(dataset_def, str):
        name = dataset_def
    else:
        name = dataset_def['name']
        lm_process_def = dataset_def.get('lm_processing')
        if lm_process_def is not None:
            # user is specifying some landmark processing
            lm_process = retrieve_lm_processes(lm_process_def)

    module = load_module_for_dataset(name)
    id_img_gen = getattr(module, 'generate_dataset')()
    # we have a hold on the loading function, but we have some base
    # pre-processing that we always perform per-image. Wrap the generator with
    # the basic pre-processing before we return it.
    id_img_gen = wrap_dataset_with_processing(id_img_gen, basic_img_process)

    if lm_process is not None:
        # the specified lm_processes needs to be added after basic processing
        # take the landmark processing and apply it to each image
        img_lm_process = partial(apply_lm_process_to_img, lm_process)
        id_img_gen = wrap_dataset_with_processing(id_img_gen, img_lm_process)

    return id_img_gen


def print_processing_status(id_img_gen):
    i = 0
    for i, (id_, image) in enumerate(id_img_gen, 1):
        print_dynamic('Processing image {} ({})'.format(i, id_))
        yield id_, image
    print_dynamic('{} images processed.'.format(i))
    print('')


class RetainIds(object):

    def __init__(self, id_img_gen):
        self.id_img_gen = id_img_gen
        self.ids = []

    def __iter__(self):
        return self

    def next(self):
        id_, img = next(self.id_img_gen)
        self.ids.append(id_)
        return img


def swallow_ids(id_img_gen):
    for _, img in id_img_gen:
        yield img


def retrieve_datasets(dataset_defs, retain_ids=False):
    # chain together a list of datasets in a row, reporting the progress as
    # we go.
    id_img_iter = print_processing_status(
        chain(*(retrieve_dataset(d) for d in dataset_defs)))
    if retain_ids:
        return RetainIds(id_img_iter)
    else:
        return swallow_ids(id_img_iter)
