import menpo.io as mio
from menpo.landmark.labels import ibug_face_68
from menpobench.dataset import managed_dataset

metadata = {
    'display_name': 'Labelled Face Parts in the Wild Trainset with iBUG68 landmarks and DLIB bounding boxes',
    'display_name_short': 'LFPW train'
}


def generate_dataset():
    with managed_dataset('lfpw') as p:
        for img in mio.import_images(p / 'trainset' / '*.png', max_images=20,
                                     normalise=False, shuffle=True):
            img.landmarks['gt'] = ibug_face_68(img.landmarks['PTS'])[1]
            # TODO make lfpw_train_dlib bounding boxes
            img.landmarks['bbox'] = img.landmarks['PTS'].lms.bounding_box()
            del img.landmarks['PTS']
            yield img.path.stem, img
