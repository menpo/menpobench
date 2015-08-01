from functools import partial
from menpobench.config import resolve_cache_dir
from menpobench.managed import WebSource, MENPO_CDN_URL, managed_asset
from menpobench.utils import create_path, extract_archive

MENPO_CDN_DATASET_URL = MENPO_CDN_URL + 'datasets/'
MENPO_GITHUB_URL_TEMPLATE = 'https://github.com/menpo/{name}/releases/download/{version}/{name}.tar.gz'

# ----------- Cache path management ---------- #

@create_path
def dataset_dir():
    return resolve_cache_dir() / 'datasets'


@create_path
def download_dataset_dir():
    return dataset_dir() / 'dlcache'


# ----------- DatasetSource Classes ---------- #

class DatasetSource(WebSource):

    def _download_cache_dir(self):
        return download_dataset_dir()


class CDNDatasetSource(DatasetSource):

    def __init__(self, name, sha1):
        url = MENPO_CDN_DATASET_URL + '{}.tar.gz'.format(name)
        super(CDNDatasetSource, self).__init__(name, url, sha1)

    def unpack(self):
        # Extracts the archive into the unpacked dir - the unpacked
        # path will then point to the folder because it is ASSUMED that the
        # archive name matches the name of the asset and therefore the asset
        # is actually completely contained inside self.unpacked_path()
        extract_archive(self.archive_path(), self._unpacked_cache_dir())


class GithubDatasetSource(DatasetSource):

    def __init__(self, name, version, sha1):
        url = MENPO_GITHUB_URL_TEMPLATE.format(name=name, version=version)
        super(GithubDatasetSource, self).__init__(name, url, sha1)

    def unpack(self):
        # Extracts the archive into the unpacked dir - the unpacked
        # path will then point to the folder because it is ASSUMED that the
        # archive name matches the name of the asset and therefore the asset
        # is actually completely contained inside self.unpacked_path()
        extract_archive(self.archive_path(), self._unpacked_cache_dir())


# --------------------------- MANAGED DATASETS ------------------------------ #
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
    lambda: GithubDatasetSource('lfpw-test', 'v2', 'a90afa0b8997dfe50d89bf361a1a2f7285c5e17a'),
    lambda: GithubDatasetSource('lfpw-train', 'v2', 'ba1a6f63b432f3e7ef0805943c699522a3029642')
]


# On import convert the list of datasets into a dict for easy access. Use this
# opportunity to verify the uniqueness of each dataset name.
MANAGED_DATASETS = {}

for dataset in _MANAGED_DATASET_LIST:
    name = dataset().name
    if name in MANAGED_DATASETS:
        raise ValueError("Error - two managed datasets with name "
                         "'{}'".format(name))
    else:
        MANAGED_DATASETS[name] = dataset


# ----------- Magic dataset contextmanager ---------- #

managed_dataset = partial(managed_asset, MANAGED_DATASETS, cleanup=True)
