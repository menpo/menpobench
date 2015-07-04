from contextlib import contextmanager
from collections import namedtuple
import shutil

import numpy as np
from menpobench import CACHE_DIR
from menpobench.utils import checksum, download_file, extract_tar


DatasetSource = namedtuple('DatasetSource', ['name', 'url', 'sha1'])

# ----------- manged datasets ---------- #

MANAGED_DATASETS = {
    'lfpw': DatasetSource('lfpw', 'cdn.menpo.org.s3.amazonaws.com/lfpw.tar.gz',
                          '5859560f8fc7de412d44619aeaba1d1287e5ede6')
}

# ----------- Cache path management ---------- #

DATASET_DIR = CACHE_DIR / 'datasets'
if not DATASET_DIR.is_dir():
    DATASET_DIR.mkdir()

DOWNLOAD_DATASET_DIR = DATASET_DIR / 'dlcache'
if not DOWNLOAD_DATASET_DIR.is_dir():
    DOWNLOAD_DATASET_DIR.mkdir()


UNPACKED_DATASET_DIR = DATASET_DIR / 'unpacked'
if not UNPACKED_DATASET_DIR.is_dir():
    UNPACKED_DATASET_DIR.mkdir()


# ----------- tar handling ---------- #

def database_tar_path(name):
    return DOWNLOAD_DATASET_DIR / '{}.tar.gz'.format(name)


def dataset_path(name):
    return UNPACKED_DATASET_DIR / name


def checksum_of_dataset(name):
    return checksum(database_tar_path(name))


def download_datset_if_needed(name, verbose=False):
    if name not in MANAGED_DATASETS:
        if verbose:
            raise ValueError("'{}' is not a managed dataset".format(name))
    info = MANAGED_DATASETS[name]
    if database_tar_path(name).is_file():
        if checksum_of_dataset(name) != info.sha1:
            if verbose:
                print("Warning: cached version of '{}' has incorrect hash - "
                      "clearing cache".format(name))
            cleanup_dataset_tar(name)
            download_datset_if_needed(name)
        else:
            if verbose:
                print("'{}' is cached and validated".format(name))
    else:
        download_file(info.url, database_tar_path(name))
        download_datset_if_needed(name)


def unpack_dataset(name):
    extract_tar(database_tar_path(name), UNPACKED_DATASET_DIR)


def cleanup_unpacked_dataset_if_present(name):
    dset_path = dataset_path(name)
    if dset_path.is_dir():
        shutil.rmtree(str(dset_path))


def cleanup_dataset_tar(name):
    database_tar_path(name).unlink()


@contextmanager
def managed_dataset(name, verbose=False):
    # Ensure the dataset in question is cached locally
    download_datset_if_needed(name, verbose=verbose)
    cleanup_unpacked_dataset_if_present(name)
    unpack_dataset(name)
    try:
        yield dataset_path(name)
    finally:
        cleanup_unpacked_dataset_if_present(name)


# ----------- image preprocessing ---------- #

def basic_preprocess(img):
    # menpobench does some basic cleanup on all images
    return img.crop_to_landmarks_proportion(0.5)


def menpo_preprocess(img):
    # for menpo methods we always want greyscale. we also don't want images
    # that are too large, and we want floating point images.
    img = img.crop_to_landmarks_proportion(0.2)
    img.pixels = np.array(img.pixels, dtype=np.float) * (1.0 / 255.0)
    if img.n_channels == 3:
        img = img.as_greyscale(mode='luminosity')
    return img
