from contextlib import contextmanager
import shutil

from menpobench.config import resolve_cache_dir
from menpobench.utils import checksum, download_file, extract_tar, create_path

MENPO_CDN_URL = 'http://cdn.menpo.org.s3.amazonaws.com/'
MENPO_CDN_DATASET_URL = MENPO_CDN_URL + 'datasets/'


class DatasetSource(object):

    def __init__(self, name, sha1):
        self.name = name
        self.sha1 = sha1


    @property
    def url(self):
        return MENPO_CDN_DATASET_URL + '{}.tar.gz'.format(self.name)


# ----------- manged datasets ---------- #
#
# Managed datasets that menpobench is aware of. These datasets will be
# downloaded from the Team Menpo CDN dynamically and used for evaluations.
#
# To prepare a dataset for inclusion in menpobench:
#
# 1. Prepare the folder for the dataset on disk as normal. Ensure only
#    pertinent files are in the dataset folder. The name of the entire dataset
#    folder should follow Python variable naming conventions - lower case words
#    seperated by underscores (e.g. `./dataset_name/`). Note that this name
#    needs to be unique among all manged datasets.
#
# 2. tar.gz the entire folder:
#      > tar -zcvf dataset_name.tar.gz ./dataset_name/
#
# 3. Record the SHA-1 checksum of the dataset archive:
#      > shasum dataset_name.tar.gz
#
# 4. Upload the dataset archive to the Team Menpo CDN contact github/jabooth
#    for details)
#
# 5. Add the dataset source to the _MANGED_DATASET_LIST below.
#
#
_MANAGED_DATASET_LIST = [
    DatasetSource('lfpw_micro', '0f34c94687e90334e012f188531157bd291d6095'),
    DatasetSource('lfpw', '5859560f8fc7de412d44619aeaba1d1287e5ede6')
]


# on import convert the list of datasets into a dict for easy access. Use this
# opportunity to verify the uniqueness of each dataset name.
MANAGED_DATASETS = {}

for dataset in _MANAGED_DATASET_LIST:
    if dataset.name in MANAGED_DATASETS:
        raise ValueError("Error - two managed datasets with name "
                         "'{}'".format(dataset.name))
    else:
        MANAGED_DATASETS[dataset.name] = dataset



# ----------- Cache path management ---------- #

@create_path
def dataset_dir():
    return resolve_cache_dir() / 'datasets'

@create_path
def download_dataset_dir():
    return dataset_dir() / 'dlcache'

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
        # if verbose:
        #     print("'{}' is already cached - checking "
        #           "integrity...".format(name))
        if checksum_of_dataset(name) != info.sha1:
            if verbose:
                print("Warning: cached version of '{}' failed checksum - "
                      "clearing cache".format(name))
            cleanup_dataset_tar(name)
            download_dataset_if_needed(name, verbose=verbose)
        else:
            # if verbose:
            #     print("'{}' checksum validated".format(name))
            return
    else:
        if verbose:
            print("'{}' managed dataset is not cached - "
                  "downloading...".format(name))
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
        print("Unpacking cached dataset '{}'".format(name))
    unpack_dataset(name)
    # if verbose:
    #     print("'{}' is unpacked".format(name))
    try:
        yield dataset_path(name)
    finally:
        cleanup_unpacked_dataset_if_present(name)
