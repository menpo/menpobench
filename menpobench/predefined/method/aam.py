from menpobench.method import MenpoFitWrapper
from menpobench.imgprocess import menpo_img_process
from menpofit.aam import AAMBuilder, LucasKanadeAAMFitter
from menpo.feature import fast_dsift


def train(img_generator):
    # clean up the images with the standard menpo preprocessing
    images = [menpo_img_process(img) for img in img_generator]
    # build the AAM
    aam = AAMBuilder(features=fast_dsift,
                     diagonal=120).build(images, verbose=True, group='gt')
    fitter = LucasKanadeAAMFitter(aam, n_shape=0.9, n_appearance=0.9)

    # return a callable that wraps the menpo fitter in order to integrate with
    # menpobench
    return MenpoFitWrapper(fitter)
