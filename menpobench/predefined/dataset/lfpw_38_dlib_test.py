import menpo.io as mio
from menpobench.dataset import managed_dataset


def generate_dataset():
    with managed_dataset('lfpw_micro') as lfpw_path:
        train_path = lfpw_path / 'testset'
        for path in train_path.glob('*.png'):
            img = mio.import_image(path, normalise=False)
            img.landmarks['gt'] = img.landmarks['PTS']
            del img.landmarks['PTS']
            yield img
