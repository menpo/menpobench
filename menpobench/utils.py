import hashlib
import platform
import subprocess
import tarfile
import tempfile
import shutil
from copy import deepcopy
from inspect import isgeneratorfunction
try:
    from urllib2 import urlopen, HTTPError  # Py2
except ImportError:
    from urllib.request import urlopen, HTTPError # Py3
import imp
import os
import zipfile
from pathlib import Path
import yaml
import json
import gzip
import random
from math import ceil, floor
from menpobench.schema import schema_error_report, schema_is_valid
from menpobench.exception import (ModuleNotFoundError, SchemaError,
                                  MissingMetadataError)
import pyrx
rx = pyrx.Factory({"register_core_types": True})


def checksum(filepath, blocksize=65536):
    r"""
    Report the SHA-1 checksum as a hex digest for a file at a path.
    """
    sha = hashlib.sha1()
    with open(str(filepath), 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            sha.update(buf)
            buf = f.read(blocksize)
    return sha.hexdigest()


def copy_and_yield(fsrc, fdst, length=1024*1024):
    """copy data from file-like object fsrc to file-like object fdst"""
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)
        yield


def download_file(url, dest_path):
    r"""
    Download a file to a path, reporting the progress with a progress bar
    """
    from menpo.visualize.textutils import print_progress, bytes_str
    req = urlopen(url)
    n_bytes = int(req.headers['content-length'])
    chunk_size_bytes = 512 * 1024
    n_items = int(ceil((1.0 * n_bytes) / chunk_size_bytes))
    prefix = 'Downloading {}'.format(bytes_str(n_bytes))
    with open(str(dest_path), 'wb') as fp:
        for _ in print_progress(copy_and_yield(req, fp,
                                               length=chunk_size_bytes),
                                n_items=n_items, show_count=False,
                                prefix=prefix):
            pass
    req.close()


def extract_tar(tar_path, dest_dir):
    r"""
    Extract a tar file to a destination
    """
    with tarfile.open(str(tar_path)) as tar:
        tar.extractall(path=str(dest_dir))


def extract_zip(zip_path, dest_dir):
    r"""
    Extract a zip file to a destination
    """
    with zipfile.PyZipFile(str(zip_path)) as z:
        z.extractall(path=str(dest_dir))


def extract_archive(path, dest_dir):
    r"""
    Extract a given archive file to a destination. Currently supports .zip
    and .tar.gz
    """
    if path.suffix == '.zip':
        return extract_zip(path, dest_dir)
    elif ''.join(path.suffixes) == '.tar.gz':
        return extract_tar(path, dest_dir)


def load_module(path):
    r"""
    Dynamically load a Python module at a given path
    """
    name = path.stem
    return imp.load_source(name, str(path))


def invoke_process(command_list):
    subprocess.check_call(command_list)


def predefined_module(name):
    return not name.endswith('.py')


def load_module_with_error_messages(module_type, predefined_f, name,
                                    metadata_schema=None):
    custom = not predefined_module(name)
    template = "custom {} at path '{}'" if custom else "predefined {} '{}'"
    msg = template.format(module_type, name)
    path = Path(name) if custom else predefined_f(name)
    try:
        module = load_module(path)
    except IOError:
        raise ModuleNotFoundError("Requested {} does not exist".format(msg))

    # have a module loaded - has a metadata check been requested?
    if metadata_schema is not None:
        # Yes - grab the metadata
        try:
            metadata = getattr(module, 'metadata')
        except AttributeError:
            raise MissingMetadataError(msg)
        else:
            if not schema_is_valid(metadata_schema, metadata):
                # there is something incorrect about the metadata - try and
                # print a helpful message.
                report = schema_error_report(metadata_schema, metadata)
                raise SchemaError('metadata', msg, report)
            else:
                return module, metadata
    else:
        return module


def load_callable_with_error_messages(module, func_name, module_name,
                                      module_type=None, generatorfunc=False):
    prefix = module_type + ' ' if module_type is not None else ''
    type_test = isgeneratorfunction if generatorfunc else callable
    type_str = 'generator function' if generatorfunc else 'callable'
    try:
        f = getattr(module, func_name)
    except AttributeError:
        raise AttributeError("{}module '{}' doesn't include a '{}' {}".format(
            prefix, module_name, func_name, type_str))
    if not type_test(f):
        raise AttributeError("{}module '{}' includes a '{}' attribute, but it "
                             "isn't a {}".format(prefix, module_name,
                                                 func_name, type_str))
    return f


def norm_path(filepath):
    r"""
    Uses all the tricks in the book to expand a path out to an absolute one.
    """
    return os.path.abspath(os.path.normpath(
        os.path.expandvars(os.path.expanduser(str(filepath)))))


def load_yaml(filepath):
    with open(norm_path(filepath), 'rt') as f:
        y = yaml.load(f)
    return y


def save_yaml(obj, filepath):
    with open(norm_path(filepath), 'wt') as f:
        yaml.dump(obj, f)


def load_json(filepath):
    s = Path(filepath).suffix
    o = gzip.open if s == '.gz' else open
    with o(norm_path(filepath), 'rt') as f:
        y = json.load(f)
    return y


def save_json(obj, filepath, pretty=False):
    kw = {'indent': 4, 'separators': (',', ': ')} if pretty else {}
    with open(norm_path(filepath), 'wt') as f:
        json.dump(obj, f, **kw)


def load_schema(filepath):
    s = load_yaml(filepath)
    return rx.make_schema(s)


def create_path(f):
    r"""Decorator for functions returning pathlib.Path objects.
    Creates the path if it does not exist.
    """

    def wrapped(*args, **kwargs):
        p = f(*args, **kwargs)
        p = Path(norm_path(p))
        if not p.is_dir():
            print("Path '{}' does not exist - creating...".format(p))
            p.mkdir()
        return p

    return wrapped


def memoize(f):
    r"""Decorator for functions taking no args that need to be memoized.
    """
    _namespace = {'result': None}

    def wrapped():
        if _namespace['result'] is None:
            _namespace['result'] = f()
        return deepcopy(_namespace['result'])

    return wrapped


def centre_str(s, c=' ', width=80):
    r"""Pad a string out to a certain width with a padding character 'c' placed
    either side of the string, centring it.
    """
    if len(s) > (width - 4):
        return s
    remaining = width - len(s) - 2  # whitespace padding
    if remaining % 2 == 0:
        # remaining space evenly divides!
        # integer division as we'll multiply with a character
        padding = remaining // 2
        return c * padding + ' ' + s + ' ' + c * padding
    else:
        # gah, will have to be a different amount left and right
        # remaining space evenly divides!
        padding = int(floor((remaining * 1.0) / 2))
        return c * (padding + 1) + ' ' + s + ' ' + c * padding


# A Singleton pattern for supplying temporary directories and having a single
# point of call for cleaning all the temporary directories up.
# Works in Python 2 & 3
class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args,
                                                                  **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    pass


class TempDirectory(Singleton):
    _directories = []

    @classmethod
    def create_new(cls):
        d = Path(tempfile.mkdtemp())
        cls._directories.append(d)
        return d

    @classmethod
    def delete_all(cls):
        for d in cls._directories:
            shutil.rmtree(str(d), ignore_errors=True)


def wrap_generator(generator, f):
    r"""Wrap a generator with a function that is invoked per-item
    """
    for x in generator:
        yield f(x)


def is_windows():
    return 'windows' in platform.system().lower()


def is_osx():
    return 'darwin' in platform.system().lower()


def is_linux():
    return 'linux' in platform.system().lower()


def randomly_exhaust(*iterables):
    # randomly_exhaust('ABC', 'DEF') --> A B F E C D
    pool = set(iterables)
    while len(pool) > 0:
        chosen = random.choice(tuple(pool))
        try:
            yield next(chosen)
        except StopIteration:
            pool.remove(chosen)
