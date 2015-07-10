from pathlib import Path
from menpobench.config import is_linux, is_osx, is_windows, custom_config_path, \
    default_config_path
from menpobench.predefined.method.yzt_iccv_2013 import invoke_process
from menpobench.utils import create_path

_POTENTIAL_RELEASES = ['2015a', '2014b', '2014a', '2013b', '2013a', '2012b',
                       '2012a']
_DEFAULT_OSX_PATHS = ['/Applications/MATLAB_R{}.app/bin/matlab']
_DEFAULT_WINDOWS_PATHS = [r'C:\Program Files\MATLAB\R{}',
                          r'C:\Program Files (x86)\MATLAB\R{}']
_DEFAULT_LINUX_PATHS = ['/usr/local/MATLAB/R{}']


_matlab_bin_path = None


class MatlabNotFoundError(BaseException):
    pass

def _which_matlab():
    return invoke_process(['which', 'matlab'])

def _check_if_matlab_bin_exists(base_paths):
    for pr in _POTENTIAL_RELEASES:
        for base_path in base_paths:
            p = Path(base_path.format(pr))
            if p.exists():
                return p
    else:
        raise MatlabNotFoundError()

def find_matlab_binary():
    if is_linux():
        matlab_path = _which_matlab()
        if not matlab_path:
            matlab_path = _check_if_matlab_bin_exists(_DEFAULT_LINUX_PATHS)
    elif is_osx():
        matlab_path = _which_matlab()
        if not matlab_path:
            matlab_path = _check_if_matlab_bin_exists(_DEFAULT_OSX_PATHS)
    elif is_windows():
        matlab_path = _check_if_matlab_bin_exists(_DEFAULT_WINDOWS_PATHS)
    else:
        raise ValueError('Unknown Operating System')

    return matlab_path


@create_path
def resolve_matlab_bin(verbose=False):
    global _matlab_bin_path
    if _matlab_bin_path is not None:
        return _matlab_bin_path
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
        # To use menpobench, a cache directory needs to be configured.
        # See menpobench.configure_cache_dir()
        raise NoMenpoBenchCacheConfigError()
    cache_dir = Path(load_yaml(config_path)['cache_dir'])
    if verbose:
        print('cache dir: {}{}'.format(cache_dir, msg))
    # cache the result so we don't keep smashing the rc file
    _cache_dir = cache_dir
    return cache_dir
