from menpobench import predefined_dir
from menpobench.lmprocess import (retrieve_lm_processes,
                                  apply_lm_process_to_img,
                                  id_of_lm_process_or_none)
from menpobench.utils import (load_module_with_error_messages, load_schema,
                              memoize, load_callable_with_error_messages,
                              predefined_module)



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


def load_and_validate_untrainable_method_module(name):
    module, metadata = load_module_with_error_messages(
        'untrainable method', predefined_untrainable_method_path, name,
        metadata_schema=method_metadata_schema())
    test = load_callable_with_error_messages(module, 'test', name,
                                             module_type='untrainable method')
    return test, metadata


def load_and_validate_trainable_method_module(name):
    module, metadata = load_module_with_error_messages(
        'trainable method', predefined_trainable_method_path, name,
        metadata_schema=method_metadata_schema())
    train = load_callable_with_error_messages(module, 'train', name,
                                              module_type='trainable method')
    return train, metadata


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

    @property
    def predefined(self):
        return predefined_module(self.name)

    def __str__(self):
        return self.name


def wrap_img_gen_with_lm_process(img_gen, lm_process):
    for img in img_gen:
        yield apply_lm_process_to_img(lm_process, img)


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

    @property
    def id(self):
        lm_pre_train_id = id_of_lm_process_or_none(self.lm_pre_train)
        lm_pre_test_id = id_of_lm_process_or_none(self.lm_pre_test)
        lm_post_test_id = id_of_lm_process_or_none(self.lm_post_test)
        return {
            'name': self.name,
            'lm_pre_train': lm_pre_train_id,
            'lm_pre_test': lm_pre_test_id,
            'lm_post_test': lm_post_test_id
        }


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

    @property
    def id(self):
        lm_pre_test_id = id_of_lm_process_or_none(self.lm_pre_test)
        lm_post_test_id = id_of_lm_process_or_none(self.lm_post_test)
        return {
            'name': self.name,
            'lm_pre_test': lm_pre_test_id,
            'lm_post_test': lm_post_test_id
        }


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
