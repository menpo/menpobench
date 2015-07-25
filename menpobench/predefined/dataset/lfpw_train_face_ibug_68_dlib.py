import menpo.io as mio
from menpo.landmark.labels import ibug_face_68
from menpobench.dataset import managed_dataset


def generate_dataset():
    with managed_dataset('lfpw') as lfpw_path:
        for path in list((lfpw_path / 'trainset').glob('*.png'))[:20]:
            img = mio.import_image(path, normalise=False)
            img.landmarks['gt'] = ibug_face_68(img.landmarks['PTS'])[1]
            img.landmarks['bbox'] = img.landmarks['PTS'].lms.bounding_box()
            del img.landmarks['PTS']
            yield path.stem, img
