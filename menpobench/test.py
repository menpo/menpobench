import nose
import sys
from menpobench.experiment import list_predefined_experiments
from menpobench.dataset import list_predefined_datasets
from menpobench.method import (list_predefined_untrainable_methods,
                               list_predefined_methods)
from menpobench.utils import TempDirectory


TRAINABLE_METHOD = """
def test_predefined_trainable_method_{0}():
    from menpobench.method import load_and_validate_trainable_method_module
    load_and_validate_trainable_method_module('{0}')

"""


UNTRAINABLE_METHOD = """
def test_predefined_untrainable_method_{0}():
    from menpobench.method import load_and_validate_untrainable_method_module
    load_and_validate_untrainable_method_module('{0}')

"""

DATASET = """
def test_predefined_dataset_{0}():
    from menpobench.dataset import load_and_validate_dataset_module
    load_and_validate_dataset_module('{0}')

"""

EXPERIMENT = """
def test_predefined_experiment_{0}():
    from menpobench.experiment import validate_predefined_experiment
    validate_predefined_experiment('{0}')

"""


# synthesise valid source code for a Python module implementing our test suite
def generate_test_suite():
    ts = []
    ts.extend([EXPERIMENT.format(x) for x in list_predefined_experiments()])
    ts.extend([DATASET.format(x) for x in list_predefined_datasets()])
    ts.extend([TRAINABLE_METHOD.format(x) for x in list_predefined_methods()])
    ts.extend([UNTRAINABLE_METHOD.format(x) for x in
               list_predefined_untrainable_methods()])
    return ''.join(ts)


# build a test suite, run it through nose, and clear up after ourselves.
def run_test_suite(verbose=False):
    ts = generate_test_suite()
    path = str(TempDirectory.create_new() / 'mb.py')
    with open(path, 'wt') as f:
        f.write(ts)
    args = ['', path]
    if verbose:
        args.append('-v')
    tests_passed = nose.run(argv=args)
    TempDirectory.delete_all()
    if tests_passed:
        sys.exit(0)
    else:
        sys.exit(1)
