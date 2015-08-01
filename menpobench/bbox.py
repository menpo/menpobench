from functools import partial
import numpy as np


def bbox_overlap_area(a, b):
    max_overlap = np.min([a.max(axis=0), b.max(axis=0)], axis=0)
    min_overlap = np.max([a.min(axis=0), b.min(axis=0)], axis=0)
    overlap_size = max_overlap - min_overlap
    if np.any(overlap_size < 0):
        return 0
    else:
        return overlap_size.prod()


def bbox_proportion_overlap(a, b):
    overlap = bbox_overlap_area(a, b)
    return overlap / bbox_area(a)


def bbox_area(b):
    return (b.max(axis=0) - b.min(axis=0)).prod()


def bbox_area_ratio(a, b):
    return bbox_area(a) / bbox_area(b)


def bbox_overlap_acceptable(gt, d):
    return (bbox_proportion_overlap(gt, d) > 0.5 and
            bbox_area_ratio(gt, d) > 0.5)


def detect_and_check(img, detector, group=None):
    gt = img.landmarks[group].lms.bounding_box()
    bad_fits = []
    for detection in detector(img):
        if bbox_overlap_acceptable(gt.points, detection.points):
            return {'d': detection, 'gt': gt}
        else:
            bad_fits.append('prop: {:.2f}, area: {:.2f}'.format(
                bbox_proportion_overlap(gt.points, detection.points),
                bbox_area_ratio(gt.points, detection.points)))
    return {'d': None, 'gt': gt}


def normalize(gt):
    from menpo.transform import Translation, NonUniformScale
    t = Translation(gt.centre()).pseudoinverse()
    s = NonUniformScale(gt.range()).pseudoinverse()
    return t.compose_before(s)


def random_instance(pca):
    weights = np.random.multivariate_normal(np.zeros_like(pca.eigenvalues),
                                            np.diag(pca.eigenvalues))
    return pca.instance(weights)


def load_dlib_detector():
    from menpodetect import load_dlib_frontal_face_detector
    detector = load_dlib_frontal_face_detector()
    return partial(detector, greyscale=False)


def load_opencv_detector():
    from menpodetect import load_opencv_frontal_face_detector
    detector = load_opencv_frontal_face_detector()
    return partial(detector, greyscale=False)


def load_pico_detector():
    from menpodetect import load_pico_frontal_face_detector
    detector = load_pico_frontal_face_detector()
    return partial(detector, greyscale=False)

_DETECTORS = {
    'dlib': load_dlib_detector,
    # 'pico': load_pico_detector,
    # 'opencv': load_opencv_detector
}


def save_bounding_boxes(pattern, detector_type, group=None,
                        sythesize_problematic=False, overwrite=False):
    import menpo.io as mio
    from menpo.landmark import LandmarkGroup
    from menpo.model import PCAModel
    try:
        detector = _DETECTORS[detector_type]()
    except KeyError:
        detector_list = ', '.join(list(_DETECTORS.keys()))
        raise ValueError('Valid detector types are: {}'.format(detector_list))
    print('Running {} detector on {}'.format(detector_type, pattern))
    bboxes = {img.path: detect_and_check(img, detector, group=group)
              for img in mio.import_images(pattern, normalise=False,
                                           verbose=True)}

    # find all the detections that failed
    problematic = filter(lambda x: x[1]['d'] is None, bboxes.items())
    print('Failed to detect {} objects'.format(len(problematic)))
    if len(problematic) > 0 and sythesize_problematic:
        print('Learning detector traits and sythesizing fits for {} '
              'images'.format(len(problematic)))
        # get the good detections
        detections = filter(lambda x: x['d'] is not None, bboxes.values())
        # normalize these to size [1, 1], centred on origin
        normed_detections = [normalize(r['gt']).apply(r['d'])
                             for r in detections]
        # build a PCA model from good detections
        pca = PCAModel(normed_detections)

        for p, r in problematic:
            # generate a new bbox offset in the normalized space by using
            # our learnt PCA basis
            d = random_instance(pca)
            # apply an inverse transform to place it on the image
            bboxes[p]['d'] = normalize(r['gt']).pseudoinverse().apply(d)
    to_save = len(bboxes)
    if not sythesize_problematic:
        to_save = to_save - len(problematic)
    print('Saving out {} {} detections'.format(to_save, detector_type))
    # All done, save out results
    for p, r in bboxes.items():
        if r['d'] is not None:
            lg = LandmarkGroup.init_with_all_label(r['d'])
            mio.export_landmark_file(lg, p.parent /
                                     (p.stem + '_{}.ljson'.format(detector_type)),
                                     overwrite=overwrite)
