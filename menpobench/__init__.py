from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from pathlib import Path
import os

CACHE_DIR = Path(os.path.expanduser('~')) / 'menpobenchcache'

if not CACHE_DIR.is_dir():
    CACHE_DIR.mkdir()


def menpobench_dir():
    r"""The path to the top of the menpobench Python package.

    Useful for locating where the data folder is stored.

    Returns
    -------
    path : ``pathlib.Path``
        The full path to the top of the menpobench package
    """
    from pathlib import Path  # to avoid cluttering the menpo.base namespace
    return Path(os.path.abspath(__file__)).parent


def predefined_dir():
    return menpobench_dir() / 'predefined'
