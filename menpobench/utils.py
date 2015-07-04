import hashlib
import tarfile
import urllib2
import shutil
import imp
import os


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


def norm_path(filepath):
    r"""
    Uses all the tricks in the book to expand a path out to an absolute one.
    """
    return os.path.abspath(os.path.normpath(
        os.path.expandvars(os.path.expanduser(str(filepath)))))
