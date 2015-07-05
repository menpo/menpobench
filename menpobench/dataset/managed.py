from contextlib import contextmanager
from collections import namedtuple
import shutil

from menpobench.config import resolve_cache_dir
from menpobench.utils import checksum, download_file, extract_tar, create_path

DatasetSource = namedtuple('DatasetSource', ['name', 'url', 'sha1'])

MENPO_CDN_URL = 'http://cdn.menpo.org.s3.amazonaws.com/'

# ----------- manged datasets ---------- #

MANAGED_DATASETS = {
    'lfpw_micro': DatasetSource('lfpw_micro', MENPO_CDN_URL + 'lfpw_micro.tar.gz',
                          '0f34c94687e90334e012f188531157bd291d6095'),
    'lfpw': DatasetSource('lfpw', MENPO_CDN_URL + 'lfpw.tar.gz',
                          '5859560f8fc7de412d44619aeaba1d1287e5ede6')
}


# ----------- Cache path management ---------- #

@create_path
def dataset_dir():
    return resolve_cache_dir() / 'datasets'

@create_path
def download_dataset_dir():
    return resolve_cache_dir() / 'dlcache'

@create_path
def unpacked_dataset_dir():
    return dataset_dir() / 'unpacked'


# ----------- tar handling ---------- #

def database_tar_path(name):
    return download_dataset_dir() / '{}.tar.gz'.format(name)


def dataset_path(name):
    return unpacked_dataset_dir() / name


def checksum_of_dataset(name):
    return checksum(database_tar_path(name))


def download_dataset_if_needed(name, verbose=False):
    if name not in MANAGED_DATASETS:
        if verbose:
            raise ValueError("'{}' is not a managed dataset".format(name))
    info = MANAGED_DATASETS[name]
    if database_tar_path(name).is_file():
        if verbose:
            print("'{}' is already cached - checking "
                  "integrity...".format(name))
        if checksum_of_dataset(name) != info.sha1:
            if verbose:
                print("Warning: cached version of '{}' failed checksum - "
                      "clearing cache".format(name))
            cleanup_dataset_tar(name)
            download_dataset_if_needed(name, verbose=verbose)
        else:
            if verbose:
                print("'{}' checksum validated".format(name))
            return
    else:
        if verbose:
            print("'{}' is not cached - downloading...".format(name))
        download_file(info.url, database_tar_path(name))
    download_dataset_if_needed(name, verbose=verbose)


def unpack_dataset(name):
    extract_tar(database_tar_path(name), unpacked_dataset_dir())


def cleanup_unpacked_dataset_if_present(name):
    dset_path = dataset_path(name)
    if dset_path.is_dir():
        shutil.rmtree(str(dset_path))


def cleanup_dataset_tar(name):
    database_tar_path(name).unlink()


@contextmanager
def managed_dataset(name, verbose=True):
    # Ensure the dataset in question is cached locally
    download_dataset_if_needed(name, verbose=verbose)
    cleanup_unpacked_dataset_if_present(name)
    if verbose:
        print("unpacking cached '{}' for use".format(name))
    unpack_dataset(name)
    if verbose:
        print("'{}' is unpacked".format(name))
    try:
        yield dataset_path(name)
    finally:
        cleanup_unpacked_dataset_if_present(name)
