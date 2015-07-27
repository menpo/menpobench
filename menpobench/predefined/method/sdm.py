from menpobench.method import MenpoFitWrapper
from menpobench.imgprocess import menpo_img_process
from menpobench.utils import wrap_generator
from functools import partial
from menpofit.fitter import noisy_shape_from_bounding_box
from menpofit.sdm import Newton, SupervisedDecentFitter
from menpo.feature import fast_dsift


metadata = {
    'display_name': 'Menpo Supervised Decent Method',
    'display_name_short': 'Menpo SDM'
}


bbox_method = partial(noisy_shape_from_bounding_box, noise_percentage=0.001)
sdm_alg = partial(Newton, alpha=0.01)


def train(img_generator):
    # clean up the images with the standard menpo pre-processing
    img_generator = wrap_generator(img_generator, menpo_img_process)
    sdm = SupervisedDescentFitter(img_generator,
                                  group='sclera',
                                  bounding_box_group='bbox',
                                  sd_algorithm_cls=sdm_alg,
                                  patch_features=fast_dsift,
                                  scales=(1, 0.5),
                                  iterations=10,
                                  patch_shape=(17, 17),
                                  n_perturbations=20,
                                  perturb_from_bounding_box=bbox_method,
                                  verbose=False,
                                  batch_size=None)

    # return a callable that wraps the menpo fitter in order to integrate with
    # menpobench
    return MenpoFitWrapper(sdm)
