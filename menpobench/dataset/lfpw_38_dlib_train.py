import menpo.io as mio
from . import managed_dataset


def generate_dataset():
    with managed_dataset('lfpw') as lfpw_path:
        train_path = lfpw_path / 'trainset'
        for path in train_path.glob('*.png'):
            img = mio.import_image(path, normalise=False)
            img.landmarks['gt'] = img.landmarks['PTS']
            del img.landmarks['PTS']
            yield img
