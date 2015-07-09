from menpobench.method.managed import managed_method
from menpofit.aam import AAMBuilder, LucasKanadeAAMFitter
from menpo.feature import dsift
from menpobench.method import MenpoFitterWrapper
from scipy.io import savemat, loadmat


def images_to_mat(images, out_path):
    image_tuples = [{'pixels': im.pixels,
                     'gt_shape': im.landmarks['gt_shape'].lms.points,
                     'bbox': im.landmarks['bbox'].lms.points}
                    for im in images]
    savemat(out_path, image_tuples)

def train(img_generator):
    with managed_method('yzt_iccv_2013') as method_path:
        # whack images into mat file
        images = list(img_generator)
        images_to_mat(images, method_path)

        # build the AAM
        aam = AAMBuilder(features=dsift,
                         normalization_diagonal=120,
                         n_levels=3).build(images, verbose=True)
        fitter = LucasKanadeAAMFitter(aam, n_shape=0.9, n_appearance=0.9)

        # return a callable that wraps the menpo fitter in order to integrate
        # with menpobench
        return MenpoFitterWrapper(fitter)
