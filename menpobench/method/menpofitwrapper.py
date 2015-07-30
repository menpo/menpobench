from menpobench.imgprocess import menpo_img_process
from .base import BenchResult


def menpofit_to_result(fr):
    return BenchResult(fr.final_shape, inital_shape=fr.initial_shape)


class MenpoFitWrapper(object):

    def __init__(self, fitter):
        self.fitter = fitter

    def __call__(self, img_generator):
        from menpo.transform import AlignmentSimilarity
        results = []
        ref_shape = self.fitter.reference_shape
        for img in img_generator:
            # note that we don't want to crop the image in our preprocessing
            # that's because the gt on the image we are passed is what will
            # be used for assessment - we will introduce large errors if this
            # is modified in size.
            img = menpo_img_process(img, crop=False)
            bbox = img.landmarks['bbox'].lms
            shape_bb = ref_shape.bounding_box()
            init_shape = AlignmentSimilarity(shape_bb, bbox).apply(ref_shape)
            menpofit_fr = self.fitter.fit(img, init_shape)
            results.append(menpofit_to_result(menpofit_fr))
        return results
