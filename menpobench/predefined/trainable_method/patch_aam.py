from menpobench.method import MenpoFitWrapper
from menpobench.imgprocess import menpo_img_process
from menpofit.aam import PatchAAM, LucasKanadeAAMFitter
from menpo.feature import fast_dsift, no_op, igo

metadata = {
    'display_name': 'Menpo Patch-Based Active Appearance Model',
    'display_name_short': 'Menpo Patch-Based AAM'
}


def train(img_generator):
    # clean up the images with the standard menpo pre-processing
    images = [menpo_img_process(img) for img in img_generator]

    # build the AAM
    aam = PatchAAM(images, group='gt', reference_shape=None,
                   holistic_features=igo, diagonal=180,
                   scales=(0.5, 1.0), patch_shape=(24, 24),
                   patch_normalisation=no_op, max_shape_components=20,
                   max_appearance_components=250, verbose=True)

    # create fitter
    fitter = LucasKanadeAAMFitter(aam, n_shape=[5, 15], n_appearance=150)
    fit_kwargs = {'max_iters': 1}

    # return a callable that wraps the menpo fitter in order to integrate with
    # menpobench
    return MenpoFitWrapper(fitter, fit_kwargs=fit_kwargs)
