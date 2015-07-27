from menpobench.method import MenpoFitWrapper
from menpobench.imgprocess import menpo_img_process
from menpofit.sdm import SDMTrainer


metadata = {
    'display_name': 'Menpo Supervised Decent Method',
    'display_name_short': 'Menpo SDM'
}


def train(img_generator):
    # clean up the images with the standard menpo pre-processing
    images = [menpo_img_process(img) for img in img_generator]
    fitter = SDMTrainer(normalization_diagonal=150,
                        downscale=1.1,
                        n_perturbations=15).train(images, verbose=True)

    # return a callable that wraps the menpo fitter in order to integrate with
    # menpobench
    return MenpoFitWrapper(fitter)
