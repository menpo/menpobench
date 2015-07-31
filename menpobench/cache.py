import hashlib
import json
import menpobench
from menpobench.config import resolve_cache_dir, load_config
from menpobench.managed import (WebSource, MENPO_CDN_URL,
                                download_asset_if_needed)
from menpobench.utils import create_path, HTTPError, load_json
from menpobench.exception import (CachedExperimentNotAvailable,
                                  MissingConfigKeyError)

MENPO_CDN_EXPERIMENT_URL = MENPO_CDN_URL + 'experiments/'


# ----------- Cache path management ---------- #

@create_path
def experiment_dir():
    return resolve_cache_dir() / 'experiments'


@create_path
def experiment_dir_for_version(version):
    return experiment_dir() / version


# ----------- DatasetSource Classes ---------- #

class CDNExperimentSource(WebSource):

    def __init__(self, name, version):
        url = MENPO_CDN_EXPERIMENT_URL + 'v{}/{}.json.gz'.format(version, name)
        self.version = version
        super(CDNExperimentSource, self).__init__(name, url, None)

    def _download_cache_dir(self):
        return experiment_dir_for_version(self.version)

    def validate_archive_checksum(self):
        # unfortunately, we can't know ahead of time the SHAs of all the
        # experiments
        return True


# ----------- Magic dataset contextmanager ---------- #


def retrieve_cached_run(id_):
    hash = hashlib.sha1(json.dumps(id_, sort_keys=True)).hexdigest()
    v = menpobench.__version__
    # if '+' in v:
    #     print('warning - skipping hash retrieval as on a development release')
    potential_asset = CDNExperimentSource(hash, v)
    try:
        download_asset_if_needed(potential_asset, verbose=True, )
    except HTTPError:
        raise CachedExperimentNotAvailable('No cached experiment available')
    else:
        return load_json(potential_asset.archive_path())


def retrieve_upload_credentials():
    c = load_config()
    if 'MENPO_CDN_S3_ACCESS_KEY' in c and 'MENPO_CDN_S3_SECRET_KEY' in c:
        return {
            'S3_ACCESS_KEY': c['MENPO_CDN_S3_ACCESS_KEY'],
            'S3_SECRET_KEY': c['MENPO_CDN_S3_SECRET_KEY']
        }
    else:
        raise MissingConfigKeyError('MENPO_CDN_S3_ACCESS_KEY and '
                                    'MENPO_CDN_S3_SECRECT_KEY both are '
                                    'needed to upload cached results')


def can_upload():
    try:
        retrieve_upload_credentials()
    except MissingConfigKeyError:
        return False
    else:
        return True


def upload_results(results):
    cred = retrieve_upload_credentials()
    print('uploading')
