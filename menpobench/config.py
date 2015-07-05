from pathlib import Path
import os
from menpobench.utils import create_path


class NoMenpoBenchConfigError(Exception):
    pass


def custom_config_path():
    return Path(os.path.expanduser('~')) / '.menpobenchrc'


def default_config_path():
    from menpobench import menpobench_dir
    return menpobench_dir() / '.menpobenchrc'


_cache_dir = None


@create_path
def resolve_cache_dir(verbose=False):
    global _cache_dir
    if _cache_dir is not None:
        return _cache_dir
    from menpobench.utils import load_yaml
    msg = ''
    custom_config = custom_config_path()
    default_config = default_config_path()
    if custom_config.is_file():
        msg = ' (set by ~/.menpobenchrc)'
        config_path = custom_config
    elif default_config.is_file():
        config_path = default_config
    else:
        raise NoMenpoBenchConfigError('To use menpobench, a cache directory '
                                      'needs to be configured. see '
                                      'menpobench.configure_cache_dir()')
    cache_dir = Path(load_yaml(config_path)['cache_dir'])
    if verbose:
        print('cache dir: {}{}'.format(cache_dir, msg))
    # cache the result so we don't keep smashing the rc file
    _cache_dir = cache_dir
    return cache_dir


def save_custom_config(c):
    from menpobench.utils import save_yaml
    save_yaml(c, custom_config_path())


def clear_custom_config():
    p = custom_config_path()
    if p.is_file():
        p.unlink()
