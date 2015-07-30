from functools import partial
from menpobench import predefined_dir
from menpobench.imgprocess import menpo_img_process
from menpobench.lmprocess import retrieve_lm_processes, apply_lm_process_to_img
from menpobench.utils import (load_module_with_error_messages, load_schema,
                              memoize)


class BenchResult(object):

    def __init__(self, final_shape, inital_shape=None):
        self.final_shape = final_shape
        self.initial_shape = inital_shape

    @property
    def has_initial_shape(self):
        return self.initial_shape is not None

    def tojson(self):
        d = {'final': self.final_shape.points.tolist()}
        if self.has_initial_shape:
            d['initial'] = self.initial_shape.points.tolist()
        return d

    def apply_lm_process(self, lm_process):
        final_shape = lm_process(self.final_shape)
        initial_shape = (lm_process(self.initial_shape) if
                         self.has_initial_shape else None)
        return BenchResult(final_shape, inital_shape=initial_shape)


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


def save_images_to_dir(images, out_path, output_ext='.jpg'):
    from menpo.visualize import print_progress
    import menpo.io as mio
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images,
                                          prefix='Saving images to disk')):
        mio.export_image(im, out_path / '{}{}'.format(k, output_ext))


def save_landmarks_to_dir(images, label, out_path, output_ext='.pts'):
    from menpo.visualize import print_progress
    import menpo.io as mio
    if not out_path.exists():
        out_path.mkdir()
    for k, im in enumerate(print_progress(images,
                                          prefix='Saving landmarks to disk')):
        mio.export_landmark_file(im.landmarks[label],
                                 out_path / '{}{}'.format(k, output_ext))


def images_to_mat(images, out_path, attach_ground_truth=False):
    import numpy as np
    from scipy.io import savemat
    as_fortran = np.asfortranarray

    image_dicts = []
    for im in images:
        bbox = im.landmarks['bbox'].lms.bounds()
        i_dict = {'pixels': as_fortran(im.rolled_channels()),
                  'bbox': as_fortran(np.array(bbox).ravel())}
        if attach_ground_truth:
            i_dict['gt'] = as_fortran(im.landmarks['gt'].lms.points)
        image_dicts.append(i_dict)

    if not out_path.exists():
        out_path.mkdir(parents=True)
    mat_out_path = out_path / 'menpobench_images.mat'
    print('Serializing image data to Matlab file: {}'.format(mat_out_path))
    savemat(str(mat_out_path), {'menpobench_images': image_dicts})


def predefined_trainable_method_dir():
    return predefined_dir() / 'trainable_method'


def predefined_untrainable_method_dir():
    return predefined_dir() / 'untrainable_method'


def predefined_trainable_method_path(name):
    return predefined_trainable_method_dir() / '{}.py'.format(name)


def predefined_untrainable_method_path(name):
    return predefined_untrainable_method_dir() / '{}.py'.format(name)


def list_predefined_trainable_methods():
    return sorted([p.stem for p in
                   predefined_trainable_method_dir().glob('*.py')])


def list_predefined_untrainable_methods():
    return sorted([p.stem for p in
                   predefined_untrainable_method_dir().glob('*.py')])


@memoize
def method_metadata_schema():
    return load_schema(predefined_dir() / 'method_metadata_schema.yaml')


_load_trainable_method_module = partial(
    load_module_with_error_messages, 'method',
    predefined_trainable_method_path,
    metadata_schema=method_metadata_schema())

_load_untrainable_method_module = partial(
    load_module_with_error_messages, 'untrainable method',
    predefined_untrainable_method_path,
    metadata_schema=method_metadata_schema())


def load_and_validate_untrainable_method_module(name):
    module, metadata = _load_untrainable_method_module(name)
    try:
        test = getattr(module, 'test')
    except AttributeError:
        raise AttributeError("untrainable method module '{}' doesn't "
                             "include a 'test' callable".format(name))
    if not callable(test):
        raise AttributeError("untrainable method module '{} includes a "
                             "'test' attribute, but it isn't a "
                             "callable".format(name))
    return test, metadata


def load_and_validate_trainable_method_module(name):
    module, metadata = _load_trainable_method_module(name)
    try:
        train = getattr(module, 'train')
    except AttributeError:
        raise AttributeError("trainable method module '{}' doesn't "
                             "include a 'train' callable".format(name))
    if not callable(train):
        raise AttributeError("trainable method module '{} includes a "
                             "'train' attribute, but it isn't a "
                             "callable".format(name))
    return train, metadata


def wrap_img_gen_with_lm_process(img_gen, lm_process):
    for img in img_gen:
        yield apply_lm_process_to_img(lm_process, img)


class Method(object):

    def __init__(self, name, metadata):
        self.name = name
        self.metadata = metadata

    @property
    def dependencies(self):
        return self.metadata.get('dependencies', [])

    @property
    def depends_on_matlab(self):
        return 'matlab' in self.dependencies

    def __str__(self):
        return self.name


class Train(Method):

    def __init__(self, train, name, metadata, lm_pre_train, lm_pre_test,
                 lm_post_test):
        super(Train, self).__init__(name, metadata)
        self.train = train
        self.lm_pre_train = lm_pre_train
        self.lm_pre_test = lm_pre_test
        self.lm_post_test = lm_post_test

    def __call__(self, img_gen):
        # Invoke the train method we hold, but make sure we apply the landmark
        # parsing around the callable
        if self.lm_pre_train is not None:
            img_gen = wrap_img_gen_with_lm_process(img_gen, self.lm_pre_train)
        # Call the train method with our (potentially wrapped) generator
        test = self.train(img_gen)
        # finally wrap the test method returned with our test landmark process
        # steps
        return Test(test, self.name, self.metadata, self.lm_pre_test,
                    self.lm_post_test)


class Test(Method):

    def __init__(self, test, name, metadata, lm_pre_test, lm_post_test):
        super(Test, self).__init__(name, metadata)
        self.test = test
        self.lm_pre_test = lm_pre_test
        self.lm_post_test = lm_post_test

    def __call__(self, img_gen):
        # Invoke the test method we hold, but make sure we apply the landmark
        # parsing around the callable
        if self.lm_pre_test is not None:
            img_gen = wrap_img_gen_with_lm_process(img_gen, self.lm_pre_test)
        results = self.test(img_gen)
        if self.lm_post_test is not None:
            results = [r.apply_lm_process(self.lm_post_test) for r in results]
        return results


def retrieve_trainable_method(method_def):
    lm_pre_test, lm_post_test, lm_pre_train = None, None, None
    if isinstance(method_def, str):
        name = method_def
    else:
        name = method_def['name']
        lm_pre_test_def = method_def.get('lm_pre_test')
        lm_post_test_def = method_def.get('lm_post_test')
        if lm_pre_test_def is not None:
            lm_pre_test = retrieve_lm_processes(lm_pre_test_def)
        if lm_post_test_def is not None:
            lm_post_test = retrieve_lm_processes(lm_post_test_def)

        lm_pre_train_def = method_def.get('lm_pre_train')
        if lm_pre_train_def is not None:
            lm_pre_train = retrieve_lm_processes(lm_pre_train_def)

    train, metadata = load_and_validate_trainable_method_module(name)
    return Train(train, name, metadata, lm_pre_train, lm_pre_test,
                 lm_post_test)


def retrieve_untrainable_method(method_def):
    lm_pre_test, lm_post_test = None, None
    if isinstance(method_def, str):
        name = method_def
    else:
        name = method_def['name']
        lm_pre_test_def = method_def.get('lm_pre_test')
        lm_post_test_def = method_def.get('lm_post_test')
        if lm_pre_test_def is not None:
            lm_pre_test = retrieve_lm_processes(lm_pre_test_def)
        if lm_post_test_def is not None:
            lm_post_test = retrieve_lm_processes(lm_post_test_def)

    test, metadata = load_and_validate_untrainable_method_module(name)
    return Test(test, name, metadata, lm_pre_test, lm_post_test)
