import numpy as np
from functools import partial
from scipy.io import savemat
import menpo.io as mio
from menpo.visualize import print_progress
from menpobench import predefined_dir
from menpobench.preprocess import menpo_preprocess
from menpobench.utils import load_module_with_error_messages


class MenpoFitterWrapper(object):

    def __init__(self, fitter):
        self.fitter = fitter

    def __call__(self, img_generator):
        results = []
        for img in img_generator:
            img = menpo_preprocess(img)
            # obtain ground truth (original) landmarks
            gt_shape = img.landmarks['gt_shape'].lms
            results.append(self.fitter.fit(img, gt_shape, gt_shape=gt_shape))
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
        # TODO: Use bbox not gt_shape
        i_dict = {'pixels': as_fortran(im.rolled_channels()),
                  'bbox': as_fortran(im.landmarks['gt_shape'].lms.points)}
        if attach_ground_truth:
            i_dict['gt_shape'] = as_fortran(im.landmarks['gt_shape'].lms.points)
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


def retrieve_method(name):
    module = load_module_for_method(name)
    return getattr(module, 'train')


def retrieve_untrainable_method(name):
    module = load_module_for_untrainable_method(name)
    return getattr(module, 'test')
