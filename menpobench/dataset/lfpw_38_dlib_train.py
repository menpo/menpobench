# ---- LFPW ----
#
# ./my_dataset
#    ./training_images
#      ./IMG_000.jpg
#      ...
#    ./gt
#      ./IMG_000.ljson
#      ...
#    ./bbox
#      ./IMG_000.ljson
#      ...
#
import menpo.io as mio
from pathlib import Path

DB_PATH = Path('/vol/atlas/database/my_dataset')


def generate_dataset():
    for path in (DB_PATH / 'training_images').glob('*.jpg'):
        im = mio.import_image(path)
        im.landmarks['gt'] = mio.import_landmark_file(DB_PATH / 'gt' / (path.stem + '.ljson'))
        im.landmarks['bbox'] = mio.import_landmark_file(DB_PATH / 'bbox' / (path.stem + '.ljson'))
        yield im