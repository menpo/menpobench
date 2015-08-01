import menpo.io as mio
from menpo.landmark.labels import ibug_face_68
from menpobench.dataset import managed_dataset

metadata = {
    'display_name': 'Labelled Face Parts in the Wild Testset with iBUG68 landmarks and DLIB bounding boxes',
    'display_name_short': 'LFPW test'
}


def _resolver(img):
    p = img.path
    return {
        'gt': p.with_suffix('.pts'),
        'bbox': p.with_name('{}_dlib.ljson'.format(p.stem))
    }


def generate_dataset():
    with managed_dataset('lfpw-test') as p:
        for img in mio.import_images(p / '*.png',
                                     normalise=False, shuffle=True,
                                     landmark_resolver=_resolver):
            img.landmarks['gt'] = ibug_face_68(img.landmarks['gt'])[1]
            yield img.path.stem, img
