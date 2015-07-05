import hashlib
import tarfile
import urllib2
import shutil
import imp
import os
from pathlib import Path
import yaml


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


def download_file(url, dest_path):
    r"""
    Download a file to a path
    """
    req = urllib2.urlopen(url)
    with open(str(dest_path), 'wb') as fp:
        shutil.copyfileobj(req, fp)
    req.close()


def extract_tar(tar_path, dest_dir):
    r"""
    Extract a tar file to a destination
    """
    with tarfile.open(str(tar_path)) as tar:
        tar.extractall(path=str(dest_dir))


def load_module(path):
    r"""
    Dynamically load a Python module at a given path
    """
    name = path.stem
    return imp.load_source(name, str(path))


def load_module_with_error_messages(module_type, predefined_f, name):
    if name.endswith('.py'):
        # custom module
        try:
            module = load_module(Path(name))
        except IOError:
            raise ValueError("Requested custom {} at path '{}' "
                             "does not exist".format(module_type, name))
    else:
        # predefined module
        try:
            module = load_module(predefined_f(name))
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
