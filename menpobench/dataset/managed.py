from functools import partial
from menpobench.config import resolve_cache_dir
from menpobench.managed import WebSource, MENPO_CDN_URL, managed_asset
from menpobench.utils import create_path


MENPO_CDN_DATASET_URL = MENPO_CDN_URL + 'datasets/'


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


# ----------- DatasetSource Classes ---------- #

class DatasetSource(WebSource):

    def __init__(self, name, url, sha1):
        super(DatasetSource, self).__init__(name, url, sha1)

    def _download_cache_dir(self):
        return download_dataset_dir()

    def _unpacked_cache_dir(self):
        return unpacked_dataset_dir()


class CDNDatasetSource(DatasetSource):

    def __init__(self, name, sha1):
        url = MENPO_CDN_DATASET_URL + '{}.tar.gz'.format(name)
        super(CDNDatasetSource, self).__init__(name, url, sha1)


# ----------- Managed Datasets ---------- #
#
# Managed datasets that menpobench is aware of. These datasets will ideally be
# downloaded from the Team Menpo CDN dynamically and used for evaluations.
#
# To prepare a dataset for inclusion in menpobench via the CDN:
#
# 1. Prepare the folder for the dataset on disk as normal. Ensure only
#    pertinent files are in the dataset folder. The name of the entire dataset
#    folder should follow Python variable naming conventions - lower case words
#    separated by underscores (e.g. `./dataset_name/`). Note that this name
#    needs to be unique among all managed datasets.
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
# 5. Add the dataset source to the _MANAGED_DATASET_LIST below as a
#    CDNDatasetSource.
#
#
_MANAGED_DATASET_LIST = [
    CDNDatasetSource('lfpw_micro', '0f34c94687e90334e012f188531157bd291d6095'),
    CDNDatasetSource('lfpw', '5859560f8fc7de412d44619aeaba1d1287e5ede6')
]


# On import convert the list of datasets into a dict for easy access. Use this
# opportunity to verify the uniqueness of each dataset name.
MANAGED_DATASETS = {}

for dataset in _MANAGED_DATASET_LIST:
    if dataset.name in MANAGED_DATASETS:
        raise ValueError("Error - two managed datasets with name "
                         "'{}'".format(dataset.name))
    else:
        MANAGED_DATASETS[dataset.name] = dataset


# ----------- Magic dataset contextmanager ---------- #

managed_dataset = partial(managed_asset, MANAGED_DATASETS)
