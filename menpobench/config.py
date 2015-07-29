import os
import platform
from pathlib import Path
from menpobench.exception import MissingConfigKeyError
from menpobench.utils import create_path, load_schema, memoize, load_yaml
from menpobench import predefined_dir
from menpobench.schema import schema_error_report, schema_is_valid
from menpobench.exception import SchemaError

def custom_config_path():
    return Path(os.path.expanduser('~')) / '.menpobenchrc'


def default_config_path():
    from menpobench import menpobench_dir
    return menpobench_dir() / '.menpobenchrc'


@memoize
def config_schema():
    return load_schema(predefined_dir() / 'config_schema.yaml')


def resolve_config_path():
    custom_config = custom_config_path()
    default_config = default_config_path()
    if custom_config.is_file():
        config_path = custom_config
    elif default_config.is_file():
        config_path = default_config
    else:
        # Create an empty default config file. Missing keys was will throw
        # a key error which can be caught so keys can be prompted.
        save_custom_config({}, validate_schema=False)
        config_path = custom_config
    return config_path


@memoize
@create_path
def resolve_cache_dir(verbose=False):
    config_path = resolve_config_path()
    try:
        cache_dir = Path(load_yaml(config_path)['cache_dir'])
    except KeyError as e:
        raise MissingConfigKeyError(e.message)
    if verbose:
        print('Cache dir: {}'.format(cache_dir))
    return cache_dir


def save_custom_config(c, validate_schema=True):
    from menpobench.utils import save_yaml, load_yaml
    if custom_config_path().exists():
        # Update existing config file with new information
        config = load_yaml(custom_config_path())
        config.update(c)
    else:
        config = c
    if validate_schema:
        # validate the config against the schema
        s = config_schema()
        if not schema_is_valid(s, config):
            report = schema_error_report(s, config)
            raise SchemaError('configuration', 'user', report)
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
