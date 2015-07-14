import os
from subprocess import CalledProcessError
from pathlib import Path
import shutil
from scipy.io import loadmat
from menpobench import configure_matlab_bin_path
from menpobench.config import (is_linux, is_osx, is_windows,
                               resolve_config_path)
from menpobench.method.base import predefined_method_dir, save_images_to_dir, save_landmarks_to_dir, images_to_mat
from menpobench.utils import invoke_process, TempDirectory

_POTENTIAL_RELEASES = ['2015a', '2014b', '2014a', '2013b', '2013a', '2012b',
                       '2012a']
_DEFAULT_OSX_PATHS = ['/Applications/MATLAB_R{}.app/bin/matlab']
_DEFAULT_WINDOWS_PATHS = [r'C:\Program Files\MATLAB\R{}\bin\matlab.exe',
                          r'C:\Program Files (x86)\MATLAB\R{}\bin\matlab.exe']
_DEFAULT_LINUX_PATHS = ['/usr/local/MATLAB/R{}/bin/matlab']


_matlab_bin_path = None


def matlab_functions_dir():
    return Path(os.path.abspath(__file__)).parent / 'matlab'


def _which_matlab():
    try:
        return invoke_process(['which', 'matlab'])
    except CalledProcessError:
        # Swallow non-zero returncode of which when not found
        pass


def _check_if_matlab_bin_exists(base_paths):
    # Prefer most recent release over older releases.
    for pr in _POTENTIAL_RELEASES:
        for base_path in base_paths:
            p = Path(base_path.format(pr))
            if p.exists():
                return p
    else:
        return ""


def find_matlab_binary():
    if is_linux():
        matlab_path = _which_matlab()
        if not matlab_path:
            matlab_path = _check_if_matlab_bin_exists(_DEFAULT_LINUX_PATHS)
    elif is_osx():
        matlab_path = _which_matlab()
        if not matlab_path:
            matlab_path = _check_if_matlab_bin_exists(_DEFAULT_OSX_PATHS)
    elif is_windows():
        matlab_path = _check_if_matlab_bin_exists(_DEFAULT_WINDOWS_PATHS)
    else:
        # Unknown operating system, just give up - user will have to set
        matlab_path = ""

    return matlab_path


def resolve_matlab_bin_path(verbose=False):
    global _matlab_bin_path
    if _matlab_bin_path is not None:
        return _matlab_bin_path

    from menpobench.utils import load_yaml
    config_path = resolve_config_path()

    try:
        # Will throw key error if matlab_bin_path does not exist
        matlab_bin_path = Path(load_yaml(config_path)['matlab_bin_path'])
    except KeyError:
        # OK, there's no known matlab path, lets be proactive and try and
        # find it ourselves
        matlab_bin_path = find_matlab_binary()
        # If we still failed, re-throw the key-error
        if not matlab_bin_path:
            raise KeyError('matlab_bin_path')
        else:  # Save the found matlab path
            if verbose:
                print('Automatically found Matlab path: {}'.format(matlab_bin_path))
            configure_matlab_bin_path(matlab_bin_path)

    if verbose:
        print('Matlab path: {}'.format(matlab_bin_path))
    # Cache the result so we don't keep querying the rc file
    _matlab_bin_path = matlab_bin_path
    return _matlab_bin_path


def invoke_matlab(command):
    matlab_bin_path = resolve_matlab_bin_path()
    invoke_process(['{}'.format(matlab_bin_path),
                    '-nosplash', '-nodesktop', '-nojvm', '-r',
                    '{}'.format(command)])


def load_matlab_results(results_path):
    return loadmat(str(results_path / 'menpobench_test_results.mat'))


class MatlabWrapper(object):

    def __init__(self, method_path):
        self.method_path = method_path

    def __call__(self, img_generator):
        test_path = TempDirectory.create_new() / 'menpobench_test_images'
        # Save images down to mat file
        images_to_mat(img_generator, test_path)

        # Call matlab bridge to test file - will drop out a result mat
        invoke_matlab("addpath('{}'); menpobench_matlab_fit('{}', '{}');".format(
            matlab_functions_dir(), self.method_path, test_path))
        
        return load_matlab_results(test_path)


def train_matlab_method(method_path, matlab_train_filename,
                        training_images_path):
    # Get absolute path to the train method and copy across to the method
    # folder
    matlab_train_path = predefined_method_dir() / matlab_train_filename
    shutil.copyfile(str(matlab_train_path),
                    str(method_path / 'menpobench_namespace.m'))

    # Call matlab bridge to train file - will drop out a model file
    invoke_matlab("addpath('{}'); menpobench_matlab_train('{}', '{}');".format(
        matlab_functions_dir(), method_path, training_images_path))
