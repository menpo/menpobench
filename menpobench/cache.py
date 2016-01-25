import hashlib
import json
import gzip
from io import BytesIO
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
        url = MENPO_CDN_EXPERIMENT_URL + '{}/{}.json.gz'.format(version, name)
        self.version = version
        super(CDNExperimentSource, self).__init__(name, url, None)

    def _download_cache_dir(self):
        return experiment_dir_for_version(self.version)

    def validate_archive_checksum(self):
        # unfortunately, we can't know ahead of time the SHAs of all the
        # experiments
        return True


# ----------- Magic dataset contextmanager ---------- #


def retrieve_results(id_):
    potential_asset = CDNExperimentSource(hash_of_id(id_), cache_version())
    try:
        download_asset_if_needed(potential_asset, verbose=True, )
    except HTTPError:
        raise CachedExperimentNotAvailable('No cached experiment available')
    else:
        return load_json(potential_asset.archive_path())


def retrieve_upload_credentials():
    c = load_config()
    if 'MENPO_CDN_S3_ACCESS_KEY' in c and 'MENPO_CDN_S3_SECRET_KEY' in c:
        return c['MENPO_CDN_S3_ACCESS_KEY'], c['MENPO_CDN_S3_SECRET_KEY']
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


def upload_results(results, id_):
    import tinys3
    print(retrieve_upload_credentials())
    conn = tinys3.Connection(*retrieve_upload_credentials(), tls=True,
                             default_bucket='cdn.menpo.org',
                             endpoint='s3-eu-west-1.amazonaws.com')
    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        json.dump(results, f)
    conn.upload('experiments/{}/{}.json.gz'.format(cache_version(),
                                                   hash_of_id(id_)), out)
    print('Successfully cached result')


def hash_of_id(id_):
    return hashlib.sha1(json.dumps(id_, sort_keys=True).encode()).hexdigest()


def cache_version():
    v = menpobench.__version__
    if '+' in v:
        return 'd' + v.split('+')[0]
    else:
        return 'v' + v
