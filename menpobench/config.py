import os
import platform
from pathlib import Path
from menpobench.exception import MissingConfigKeyError
from menpobench.utils import create_path


def custom_config_path():
    return Path(os.path.expanduser('~')) / '.menpobenchrc'


def default_config_path():
    from menpobench import menpobench_dir
    return menpobench_dir() / '.menpobenchrc'


_cache_dir = None


def resolve_config_path():
    custom_config = custom_config_path()
    default_config = default_config_path()
    if custom_config.is_file():
        config_path = custom_config
    elif default_config.is_file():
        config_path = default_config
    else:
        # Create an empty default config file. Mising keys was will throw
        # a key error which can be caught so keys can be prompted.
        save_custom_config({})
        config_path = custom_config
    return config_path


@create_path
def resolve_cache_dir(verbose=False):
    global _cache_dir
    if _cache_dir is not None:
        return _cache_dir

    from menpobench.utils import load_yaml
    config_path = resolve_config_path()
    try:
        cache_dir = Path(load_yaml(config_path)['cache_dir'])
    except KeyError as e:
        raise MissingConfigKeyError(e.message)
    if verbose:
        print('Cache dir: {}'.format(cache_dir))
    # Cache the result so we don't keep querying the rc file
    _cache_dir = cache_dir
    return cache_dir


def save_custom_config(c):
    from menpobench.utils import save_yaml, load_yaml
    if custom_config_path().exists():
        # Update existing config file with new information
        config = load_yaml(custom_config_path())
        config.update(c)
    else:
        config = c
    save_yaml(config, custom_config_path())


def clear_custom_config():
    p = custom_config_path()
    if p.is_file():
        p.unlink()


def is_windows():
    return 'windows' in platform.system().lower()


def is_osx():
    return 'darwin' in platform.system().lower()


def is_linux():
    return 'linux' in platform.system().lower()
