from .base import train


class MenpoFitterWrapper(object):

    def __init__(self, fitter):
        self.fitter = fitter

    def __call__(self, img):
        return self.fitter.fit(img)
