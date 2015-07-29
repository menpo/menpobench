import menpo.io as mio
from menpo.landmark.labels import ibug_face_68
from menpobench.dataset import managed_dataset

metadata = {
    'display_name': 'Labelled Face Parts in the Wild Trainset with iBUG68 landmarks and DLIB bounding boxes',
    'display_name_short': 'LFPW train'
}


def generate_dataset():
    with managed_dataset('lfpw') as lfpw_path:
        for path in (lfpw_path / 'trainset').glob('*.png'):
            img = mio.import_image(path, normalise=False)
            img.landmarks['gt'] = ibug_face_68(img.landmarks['PTS'])[1]
            # TODO make lfpw_train_dlib bounding boxes
            img.landmarks['bbox'] = img.landmarks['PTS'].lms.bounding_box()
            del img.landmarks['PTS']
            yield path.stem, img
