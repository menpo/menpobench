import hashlib
import tarfile
import urllib2
import shutil
import imp
import os


def checksum(fname, blocksize=65536):
    sha = hashlib.sha1()
    with open(str(fname), 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            sha.update(buf)
            buf = f.read(blocksize)
    return sha.hexdigest()


def download_file(url, path_to_download):
    req = urllib2.urlopen(url)
    with open(str(path_to_download), 'wb') as fp:
        shutil.copyfileobj(req, fp)
    req.close()


def extract_tar(fname, destination):
    with tarfile.open(str(fname)) as tar:
        tar.extractall(path=str(destination))


def load_module(path):
    name = path.stem
    return imp.load_source(name, str(path))


def norm_path(filepath):
    r"""
    Uses all the tricks in the book to expand a path out to an absolute one.
    """
    return os.path.abspath(os.path.normpath(
        os.path.expandvars(os.path.expanduser(str(filepath)))))
