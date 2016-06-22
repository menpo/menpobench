from menpobench.method import MenpoFitWrapper
from menpobench.imgprocess import menpo_img_process
from menpofit.aam import HolisticAAM, LucasKanadeAAMFitter
from menpo.feature import fast_dsift

metadata = {
    'display_name': 'Menpo Active Appearance Model',
    'display_name_short': 'Menpo AAM'
}


def train(img_generator):
    # clean up the images with the standard menpo pre-processing
    images = [menpo_img_process(img) for img in img_generator]

    # build the AAM
    aam = HolisticAAM(images, group='gt', reference_shape=None,
                      holistic_features=fast_dsift, diagonal=180,
                      scales=(0.25, 0.5, 1.0), max_shape_components=20,
                      max_appearance_components=250, verbose=True)

    # create fitter
    fitter = LucasKanadeAAMFitter(aam, n_shape=[5, 10, 15], n_appearance=150)
    fit_kwargs = {'max_iters': 75}

    # return a callable that wraps the menpo fitter in order to integrate with
    # menpobench
    return MenpoFitWrapper(fitter, fit_kwargs=fit_kwargs)
