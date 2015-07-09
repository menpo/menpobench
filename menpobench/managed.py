from contextlib import contextmanager
import shutil
from pathlib import Path

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from menpobench.utils import extract_archive, checksum, download_file, \
    TempDirectory


# Global url for the current Menpo CDN for storing assets - datasets and
# third party binaries
MENPO_CDN_URL = 'http://cdn.menpo.org.s3.amazonaws.com/'


# ----------- DatasetSource Classes ---------- #

class AssetSource(object):

    def __init__(self, name):
        super(AssetSource, self).__init__()
        self.name = name
        self._unpacked_temp_dir = None

    def _download_cache_dir(self):
        raise NotImplementedError()

    def _unpacked_cache_dir(self):
        if self._unpacked_temp_dir is None:
            self._unpacked_temp_dir = TempDirectory.create_new()
        return self._unpacked_temp_dir

    def unpacked_path(self):
        return self._unpacked_cache_dir() / self.name

    def cleanup_unpacked_data_if_present(self):
        dset_path = self.unpacked_path()
        if dset_path.is_dir():
            shutil.rmtree(str(dset_path))

    def unpack(self):
        raise NotImplementedError()


class WebSource(AssetSource):

    def __init__(self, name, url, sha1):
        super(WebSource, self).__init__(name)
        self.sha1 = sha1
        self.url = url
        self.archive_suffix = ''.join(Path(urlparse(url).path).suffixes)

    def cleanup_archive(self):
        self.archive_path().unlink()

    def archive_path(self):
        return self._download_cache_dir() / '{}{}'.format(self.name,
                                                          self.archive_suffix)

    def archive_checksum(self):
        return checksum(self.archive_path())

    def validate_archive_checksum(self):
        return self.archive_checksum() == self.sha1

    def unpack(self):
        extract_archive(self.archive_path(), self._unpacked_cache_dir())


class LocalSource(AssetSource):

    def __init__(self, name, local_path):
        super(LocalSource, self).__init__(name)
        self.local_path = local_path

    def unpack(self):
        folder_name = self.local_path.name
        shutil.copytree(self.local_path,
                        self._unpacked_cache_dir() / folder_name,
                        symlinks=True)


def get_asset(name, asset_set):
    if name not in asset_set:
        raise ValueError("'{}' is not a managed dataset".format(name))
    else:
        return asset_set[name]


def download_asset_if_needed(asset, verbose=False, checksum_fail=False):
    if asset.archive_path().is_file():
        if not asset.validate_archive_checksum():
            if verbose:
                print("Warning: cached version of '{}' failed checksum - "
                      "clearing cache".format(asset.name))

            actual_checksum = asset.archive_checksum()
            asset.cleanup_archive()

            if not checksum_fail:
                download_asset_if_needed(asset, verbose=verbose,
                                         checksum_fail=True)
            else:
                raise ValueError('Unable to download asset - checksum does '
                                 'not match expected: {} != {} '
                                 '(actual != expected)'.format(actual_checksum,
                                                               asset.sha1))
        else:
            return
    else:
        if verbose:
            print("'{}' managed asset is not cached - "
                  "downloading...".format(asset.name))
        download_file(asset.url, asset.archive_path())
    download_asset_if_needed(asset, verbose=verbose,
                             checksum_fail=checksum_fail)


@contextmanager
def managed_asset(asset_set, name, verbose=True, cleanup=True):
    asset = get_asset(name, asset_set)
    # Ensure the asset in question is cached locally
    download_asset_if_needed(asset, verbose=verbose)
    if verbose:
        print("Unpacking cached asset '{}' to {}".format(name,
                                                         asset.unpacked_path()))
    asset.unpack()
    try:
        yield asset.unpacked_path()
    finally:
        if cleanup:
            asset.cleanup_unpacked_data_if_present()
