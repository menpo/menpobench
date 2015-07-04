from menpobench.dataset import menpo_preprocess
from menpofit.aam import AAMBuilder, LucasKanadeAAMFitter
from menpo.feature import dsift
from . import MenpoFitterWrapper


def train(images):
    # clean up the
    images = [menpo_preprocess(img) for img in images]
    # build the AAM
    aam = AAMBuilder(features=dsift,
                     normalization_diagonal=120,
                     n_levels=3).build(images, verbose=True)
    fitter = LucasKanadeAAMFitter(aam, n_shape=0.9, n_appearance=0.9)

    # return a callable that wraps the menpo fitter in order to integrate with
    # menpobench
    return MenpoFitterWrapper(fitter)
