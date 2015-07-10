from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def configure_cache_dir(cache_dir):
    r"""Setup menpobench by configuring a directory for caching datasets and
    methods. datasets are generally large, so you will want to choose a
    directory on a volume with a fairly large capacity (we recommend 20GB+).

    Your preference will be saved at '~/.menpobenchrc', and used for future
    uses of menpobench.
    """
    from menpobench.config import save_custom_config
    save_custom_config({'cache_dir': cache_dir})


def menpobench_dir():
    r"""The path to the top of the menpobench Python package.

    Useful for locating where the data folder is stored.

    Returns
    -------
    path : ``pathlib.Path``
        The full path to the top of the menpobench package
    """
    from pathlib import Path  # to avoid cluttering the menpo.base namespace
    import os
    return Path(os.path.abspath(__file__)).parent


def predefined_dir():
    return menpobench_dir() / 'predefined'


from .base import invoke_benchmark
