from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from pathlib import Path
import os

CACHE_DIR = Path(os.path.expanduser('~')) / 'menpobenchcache'

if not CACHE_DIR.is_dir():
    CACHE_DIR.mkdir()
