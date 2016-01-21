from menpobench.imgprocess import menpo_img_process
from .base import BenchResult


def menpofit_to_result(fr):
    return BenchResult(fr.final_shape, inital_shape=fr.initial_shape)


class MenpoFitWrapper(object):

    def __init__(self, fitter, fit_kwargs=None):
        self.fitter = fitter
        self.fit_kwargs = {}
        if fit_kwargs is not None:
            self.fit_kwargs = fit_kwargs

    def __call__(self, img_generator):
        results = []
        for img in img_generator:
            # note that we don't want to crop the image in our preprocessing
            # that's because the gt on the image we are passed is what will
            # be used for assessment - we will introduce large errors if this
            # is modified in size.
            img = menpo_img_process(img, crop=False)
            bbox = img.landmarks['bbox'].lms
            menpofit_fr = self.fitter.fit_from_bb(img, bbox, **self.fit_kwargs)
            results.append(menpofit_to_result(menpofit_fr))
        return results
