from math import floor
import menpobench
from menpobench.config import resolve_cache_dir
from menpobench.dataset import retrieve_datasets
from menpobench.method import retrieve_method, retrieve_untrainable_method
from menpobench.experiment import load_experiment


def invoke_benchmark(experiment_name):
    r"""
    Invoke a benchmark specified with a configuration c
    """
    c = load_experiment(experiment_name)
    # Loop over all requested methods, training and testing them.
    # Note that methods are, by definition trainable.
    print('')
    print(centre_with_padding('- - - -  M E N P O B E N C H  - - - -'))
    print(centre_with_padding('v' + menpobench.__version__))
    print(centre_with_padding('config: {}'.format(experiment_name)))
    print(centre_with_padding('cache: {}'.format(resolve_cache_dir())))
    print('')
    if 'methods' in c:
        print(centre_with_padding('I. TRAINABLE METHODS'))
        n_methods = len(c['methods'])
        for i, m in enumerate(c['methods'], 1):
            print(centre_with_padding('{}/{} - {}'.format(i, n_methods, m), c='='))

            # A. Training
            train = retrieve_method(m)
            training_generator = retrieve_datasets(c['training_data'])
            print(centre_with_padding('training', c='-'))
            print("Training '{}' with {}".format(m, ', '.join(
                "'" + d + "'" for d in c['training_data'])))
            test = train(training_generator)
            print("Training of '{}' completed.".format(m))

            # B. Testing
            testing_generator = retrieve_datasets(c['testing_data'])
            print(centre_with_padding('testing', c='-'))
            print("Testing '{}' with {}".format(m, ', '.join(
                "'" + d + "'" for d in c['testing_data'])))
            results = test(testing_generator)

    # Untrainable methods cannot be trained, so we can only test them with
    # the test data.
    if 'untrainable_methods' in c:
        print(centre_with_padding('II. UNTRAINABLE METHODS', c=' '))
        for m in c['untrainable_methods']:
            test = retrieve_untrainable_method(m)
            testing_generator = retrieve_datasets(c['testing_data'])
            results = test(testing_generator)


def centre_with_padding(s, c=' ', width=80):
    if len(s) > (width - 4):
        return s
    remaining = width - len(s) - 2  # whitespace padding
    if remaining % 2 == 0:
        # remaining space evenly divides!
        padding = remaining / 2
        return c * padding + ' ' + s + ' ' + c * padding
    else:
        # gah, will have to be a different amount left and right
        # remaining space evenly divides!
        padding = int(floor((remaining * 1.0) / 2))
        return c * (padding + 1) + ' ' + s + ' ' + c * padding
