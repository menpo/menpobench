import numpy as np
from menpo.visualize import print_progress
import menpo.io as mio
from menpobench.method.managed import managed_method
from scipy.io import savemat, loadmat
from menpobench.method.matlab.base import train_matlab_method, MatlabWrapper


def images_to_mat(images, out_path):
    as_fortran = np.asfortranarray
    image_tuples = [{'pixels': as_fortran(im.rolled_channels()),
                     'gt_shape': as_fortran(im.landmarks['gt_shape'].lms.points),
                     # TODO: use bbox
                     'bbox': as_fortran(im.landmarks['gt_shape'].lms.points)}
                    for im in images]

    mat_out_path = out_path / 'menpobench_training_images.mat'
    print('Serializing training data to Matlab file: {}'.format(mat_out_path))
    savemat(str(mat_out_path), {'menpobench_training_images': image_tuples})


def save_images_to_dir(images, out_path, output_ext='.jpg'):
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images)):
        mio.export_image(im, out_path / '{}{}'.format(k, output_ext))


def save_landmarks_to_dir(images, label, out_path, output_ext='.pts'):
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images)):
        mio.export_landmark_file(im.landmarks[label],
                                 out_path / '{}{}'.format(k, output_ext))


def train(img_generator):
    with managed_method('yzt_iccv_2013', cleanup=False) as method_path:
        train_path = method_path / 'menpobench_train_images'
        images = list(img_generator)

        save_images_to_dir(images, train_path)
        save_landmarks_to_dir(images, 'gt_shape', train_path)

        train_matlab_method(method_path, 'yzt_iccv_2013.m', train_path)

        # return a callable that wraps the matlab fitter in order to integrate
        # with menpobench
        return MatlabWrapper(None)
