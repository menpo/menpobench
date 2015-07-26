import numpy as np
from functools import partial
from scipy.io import savemat
import menpo.io as mio
from menpo.visualize import print_progress
from menpobench import predefined_dir
from menpobench.imgprocess import menpo_img_process
from menpobench.lmprocess import retrieve_lm_processes, apply_lm_process_to_img
from menpobench.utils import (load_module_with_error_messages, load_schema,
                              memoize)


class BenchResult(object):

    def __init__(self, final_shape, inital_shape=None):
        self.final_shape = final_shape
        self.initial_shape = inital_shape

    @property
    def has_initial_shape(self):
        return self.initial_shape is not None

    def tojson(self):
        d = {'final': self.final_shape.points.tolist()}
        if self.has_initial_shape:
            d['initial'] = self.initial_shape.points.tolist()
        return d

    def apply_lm_process(self, lm_process):
        final_shape = lm_process(self.final_shape)
        initial_shape = (lm_process(self.initial_shape) if
                         self.has_initial_shape else None)
        return BenchResult(final_shape, inital_shape=initial_shape)


def menpofit_to_result(fr):
    return BenchResult(fr.final_shape, inital_shape=fr.initial_shape)


class MenpoFitWrapper(object):

    def __init__(self, fitter):
        self.fitter = fitter

    def __call__(self, img_generator):
        from menpofit.fitter import align_shape_with_bounding_box
        results = []
        ref_shape = self.fitter.reference_shape
        for img in img_generator:
            img = menpo_img_process(img)
            # obtain ground truth (original) landmarks
            bbox = img.landmarks['bbox'].lms
            init_shape = align_shape_with_bounding_box(ref_shape, bbox)
            menpofit_fr = self.fitter.fit(img, init_shape)
            results.append(menpofit_to_result(menpofit_fr))
        return results


def save_images_to_dir(images, out_path, output_ext='.jpg'):
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images,
                                          prefix='Saving images to disk')):
        mio.export_image(im, out_path / '{}{}'.format(k, output_ext))


def save_landmarks_to_dir(images, label, out_path, output_ext='.pts'):
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images,
                                          prefix='Saving landmarks to disk')):
        mio.export_landmark_file(im.landmarks[label],
                                 out_path / '{}{}'.format(k, output_ext))


def images_to_mat(images, out_path, attach_ground_truth=False):
    as_fortran = np.asfortranarray

    image_dicts = []
    for im in images:
        bbox = im.landmarks['bbox'].lms.bounds()
        i_dict = {'pixels': as_fortran(im.rolled_channels()),
                  'bbox': as_fortran(np.array(bbox).ravel())}
        if attach_ground_truth:
            i_dict['gt'] = as_fortran(im.landmarks['gt'].lms.points)
        image_dicts.append(i_dict)

    if not out_path.exists():
        out_path.mkdir(parents=True)
    mat_out_path = out_path / 'menpobench_images.mat'
    print('Serializing image data to Matlab file: {}'.format(mat_out_path))
    savemat(str(mat_out_path), {'menpobench_images': image_dicts})


def predefined_method_dir():
    return predefined_dir() / 'method'


def predefined_untrainable_method_dir():
    return predefined_dir() / 'untrainable_method'


def predefined_method_path(name):
    return predefined_method_dir() / '{}.py'.format(name)


def predefined_untrainable_method_path(name):
    return predefined_untrainable_method_dir() / '{}.py'.format(name)


def list_predefined_methods():
    return sorted([p.stem for p in predefined_method_dir().glob('*.py')])


def list_predefined_untrainable_methods():
    return sorted([p.stem for p in
                   predefined_untrainable_method_dir().glob('*.py')])


load_module_for_method = partial(load_module_with_error_messages,
                                 'method', predefined_method_path)

load_module_for_untrainable_method = partial(
    load_module_with_error_messages, 'untrainable method',
    predefined_untrainable_method_path)


def wrap_img_gen_with_lm_process(img_gen, lm_process):
    for img in img_gen:
        yield apply_lm_process_to_img(lm_process, img)


class TrainMethodLmProcessWrapper(object):

    def __init__(self, train, lm_pre_train, lm_pre_test, lm_post_test):
        self.train = train
        self.lm_pre_train = lm_pre_train
        self.lm_pre_test = lm_pre_test
        self.lm_post_test = lm_post_test

    def __call__(self, img_gen):
        # Invoke the train method we hold, but make sure we apply the landmark
        # parsing around the callable
        if self.lm_pre_train is not None:
            img_gen = wrap_img_gen_with_lm_process(img_gen, self.lm_pre_train)
        # Call the train method with our (potentially wrapped) generator
        test = self.train(img_gen)
        # finally wrap the test method returned with our test landmark process
        # steps
        return TestMethodLmProcessWrapper(test, self.lm_pre_test,
                                          self.lm_post_test)


class TestMethodLmProcessWrapper(object):

    def __init__(self, test, lm_pre_test, lm_post_test):
        self.test = test
        self.lm_pre_test = lm_pre_test
        self.lm_post_test = lm_post_test

    def __call__(self, img_gen):
        # Invoke the test method we hold, but make sure we apply the landmark
        # parsing around the callable
        if self.lm_pre_test is not None:
            img_gen = wrap_img_gen_with_lm_process(img_gen, self.lm_pre_test)
        results = self.test(img_gen)
        if self.lm_post_test is not None:
            results = [r.apply_lm_process(self.lm_post_test) for r in results]
        return results


def retrieve_method(method_def):
    lm_pre_test, lm_post_test, lm_pre_train = None, None, None
    if isinstance(method_def, str):
        name = method_def
    else:
        name = method_def['name']
        lm_pre_test_def = method_def.get('lm_pre_test')
        lm_post_test_def = method_def.get('lm_post_test')
        if lm_pre_test_def is not None:
            lm_pre_test = retrieve_lm_processes(lm_pre_test_def)
        if lm_post_test_def is not None:
            lm_post_test = retrieve_lm_processes(lm_post_test_def)

        lm_pre_train_def = method_def.get('lm_pre_train')
        if lm_pre_train_def is not None:
            lm_pre_train = retrieve_lm_processes(lm_pre_train_def)

    module = load_module_for_method(name)
    train = getattr(module, 'train')
    return TrainMethodLmProcessWrapper(train, lm_pre_train, lm_pre_test,
                                       lm_post_test), name


def retrieve_untrainable_method(method_def):
    lm_pre_test, lm_post_test = None, None
    if isinstance(method_def, str):
        name = method_def
    else:
        name = method_def['name']
        lm_pre_test_def = method_def.get('lm_pre_test')
        lm_post_test_def = method_def.get('lm_post_test')
        if lm_pre_test_def is not None:
            lm_pre_test = retrieve_lm_processes(lm_pre_test_def)
        if lm_post_test_def is not None:
            lm_post_test = retrieve_lm_processes(lm_post_test_def)

    module = load_module_for_method(name)
    train = getattr(module, 'test')
    return TestMethodLmProcessWrapper(train, lm_pre_test, lm_post_test), name


@memoize
def method_metadata_schema():
    return load_schema(predefined_dir() / 'method_metadata_schema.yaml')
