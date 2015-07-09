from functools import partial
from menpobench.config import resolve_cache_dir
from menpobench.managed import WebSource, MENPO_CDN_URL, managed_asset
from menpobench.utils import create_path


MENPO_CDN_METHODS_URL = MENPO_CDN_URL + 'methods/'


# ----------- Cache path management ---------- #

@create_path
def methods_dir():
    return resolve_cache_dir() / 'methods'


@create_path
def download_methods_dir():
    return methods_dir() / 'dlcache'


# ----------- MethodSource Classes ---------- #

class MethodSource(WebSource):

    def __init__(self, name, url, sha1):
        super(MethodSource, self).__init__(name, url, sha1)

    def _download_cache_dir(self):
        return download_methods_dir()


class CDNMethodsSource(MethodSource):

    def __init__(self, name, sha1):
        url = MENPO_CDN_METHODS_URL + '{}.tar.gz'.format(name)
        super(CDNMethodsSource, self).__init__(name, url, sha1)


# ----------- Managed Methods ---------- #
#
# Managed methods that menpobench is aware of. These methods will ideally be
# downloaded from the Team Menpo CDN dynamically and used for evaluations.
#
# To prepare a method for inclusion in menpobench via the CDN:
#
# 1. Prepare the folder for the method on disk as normal. Ensure only
#    pertinent files are in the method folder. The name of the entire method
#    folder should follow Python variable naming conventions - lower case words
#    separated by underscores (e.g. `./method_name/`). Note that this name
#    needs to be unique among all managed methods.
#
# 2. tar.gz the entire folder:
#      > tar -zcvf method_name.tar.gz ./method_name/
#
# 3. Record the SHA-1 checksum of the method archive:
#      > shasum method_name.tar.gz
#
# 4. Upload the dataset archive to the Team Menpo CDN contact github/jabooth
#    for details)
#
# 5. Add the dataset source to the _MANAGED_METHODS_LIST below as a
#    CDNMethodsSource.
#
#
_MANAGED_METHODS_LIST = [
    MethodSource('yzt_iccv_2013',
                 'http://uk.mathworks.com/matlabcentral/fileexchange/downloads/19680/akamai/tzimiro_ICCV2013_code.zip',
                 '29bc28a684c25c4f008d79b35543ba04')
]


# On import convert the list of methods into a dict for easy access. Use this
# opportunity to verify the uniqueness of each method name.
MANAGED_METHODS = {}

for dataset in _MANAGED_METHODS_LIST:
    if dataset.name in MANAGED_METHODS:
        raise ValueError("Error - two managed methods with name "
                         "'{}'".format(dataset.name))
    else:
        MANAGED_METHODS[dataset.name] = dataset


# ----------- Magic method contextmanager ---------- #

managed_method = partial(managed_asset, MANAGED_METHODS)
