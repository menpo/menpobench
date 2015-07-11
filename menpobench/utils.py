import hashlib
import subprocess
import tarfile
import tempfile
import shutil
import urllib2
import imp
import os
import zipfile
from pathlib import Path
import yaml
from math import ceil, floor
from menpo.visualize.textutils import print_progress, bytes_str


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
    req = urllib2.urlopen(url)
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
    print(' '.join(command_list))
    subprocess.check_call(command_list)


def load_module_with_error_messages(module_type, predefined_f, name):
    if name.endswith('.py'):
        # custom module
        try:
            module = load_module(Path(name))
            # print("Loaded custom {} from '{}'".format(module_type, name))
        except IOError:
            raise ValueError("Requested custom {} at path '{}' "
                             "does not exist".format(module_type, name))
    else:
        # predefined module
        try:
            module = load_module(predefined_f(name))
            # print("Loaded predefined {} '{}'".format(module_type, name))
        except IOError:
            raise ValueError("Requested predefined {} '{}' "
                             "does not exist".format(module_type, name))
    return module


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


def centre_str(s, c=' ', width=80):
    r"""Pad a string out to a certain width with a padding character 'c' placed
    either side of the string, centring it.
    """
    if len(s) > (width - 4):
        return s
    remaining = width - len(s) - 2  # whitespace padding
    if remaining % 2 == 0:
        # remaining space evenly divides!
        padding = remaining / 2
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

