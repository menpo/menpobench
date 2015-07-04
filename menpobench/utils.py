import hashlib
import tarfile
import urllib2


def checksum(fname, blocksize=65536):
    sha = hashlib.sha1()
    with open(str(fname), 'rb') as f:
        buf = f.read(blocksize)
        while len(buf) > 0:
            sha.update(buf)
            buf = f.read(blocksize)
    return sha.hexdigest()


def download_file(url, path_to_download):
    f = urllib2.urlopen(url)
    with open(path_to_download, 'wb') as fp:
        fp.write(f.read())
    fp.close()


def extract_tar(fname, destination):
    with tarfile.open(str(fname)) as tar:
        tar.extractall(path=str(destination))
