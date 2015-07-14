import menpo.io as mio
from menpobench.dataset import managed_dataset


def generate_dataset():
    with managed_dataset('lfpw') as lfpw_path:
        for path in (lfpw_path / 'trainset').glob('*.png'):
            img = mio.import_image(path, normalise=False)
            img.landmarks['gt'] = img.landmarks['PTS']
            img.landmarks['bbox'] = img.landmarks['PTS'].lms.bounding_box()
            del img.landmarks['PTS']
            yield img
