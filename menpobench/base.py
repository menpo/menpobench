from pathlib import Path
import menpobench
import shutil
from menpobench.config import resolve_cache_dir
from menpobench.dataset import retrieve_datasets
from menpobench.experiment import load_experiment, experiment_is_valid
from menpobench.method import retrieve_method, retrieve_untrainable_method
from menpobench.output import save_test_results
from menpobench.utils import centre_str, TempDirectory, norm_path, save_yaml


def invoke_benchmark(experiment_name, output_dir, overwrite=False,
                     matlab=False):
    r"""
    Invoke a benchmark specified with a configuration c
    """
    print('')
    print(centre_str('- - - -  M E N P O B E N C H  - - - -'))
    print(centre_str('v' + menpobench.__version__))
    print(centre_str('config: {}'.format(experiment_name)))
    print(centre_str('output: {}'.format(output_dir)))
    print(centre_str('cache: {}'.format(resolve_cache_dir())))
    print('')
    # Load the experiment and check it's schematically valid
    c = load_experiment(experiment_name)
    if not experiment_is_valid(c):
        raise ValueError("There is some mistake in the schema for experiment "
                         "'{}'.\nTry commenting out parts of the config to "
                         "find the problem.".format(experiment_name))
    # Handle the creation of the output directory
    output_dir_p = Path(norm_path(output_dir))
    if output_dir_p.is_dir():
        if not overwrite:
            raise ValueError("Output directory {} already exists.\n"
                             "Pass '--overwrite' if you want menpobench to "
                             "delete this directory "
                             "automatically.".format(output_dir))
        else:
            print('--overwrite passed and output directory {} exists - '
                  'deleting'.format(output_dir))
            shutil.rmtree(str(output_dir_p))
    output_dir_p.mkdir()
    methods_dir = output_dir_p / 'methods'
    untrainable_dir = output_dir_p / 'untrainable_methods'
    save_yaml(c, str(output_dir_p / 'experiment.yaml'))
    # Loop over all requested methods, training and testing them.
    # Note that methods are, by definition trainable.
    try:
        if 'methods' in c:
            methods_dir.mkdir()
            print(centre_str('I. TRAINABLE METHODS'))
            n_methods = len(c['methods'])

            for i, m in enumerate(c['methods'], 1):
                print(centre_str('{}/{} - {}'.format(i, n_methods, m), c='='))

                # A. Training
                train, method_name = retrieve_method(m)
                trainset = retrieve_datasets(c['training_data'])
                print(centre_str('training', c='-'))
                print("Training '{}' with {}".format(method_name, ', '.join(
                    "'{}'".format(d) for d in c['training_data'])))
                test = train(trainset)
                print("Training of '{}' completed.".format(m))

                # B. Testing
                # We elect to retain the ids for each of the test images.
                # We can use them later on to connect the results back to
                # specific images.
                testset = retrieve_datasets(c['testing_data'], retain_ids=True)
                print(centre_str('testing', c='-'))
                print("Testing '{}' with {}".format(method_name, ', '.join(
                    "'{}'".format(d) for d in c['testing_data'])))
                results = {i: r for i, r in zip(testset.ids, test(testset))}
                save_test_results(results, method_name, methods_dir,
                                  matlab=matlab)

        # Untrainable methods cannot be trained, so we can only test them with
        # the test data.
        if 'untrainable_methods' in c:
            untrainable_dir.mkdir()
            print(centre_str('II. UNTRAINABLE METHODS', c=' '))
            for m in c['untrainable_methods']:
                test, method_name = retrieve_untrainable_method(m)
                testset = retrieve_datasets(c['testing_data'], retain_ids=True)
                print(centre_str('testing', c='-'))
                print("Testing '{}' with {}".format(m, ', '.join(
                    "'{}'".format(d) for d in c['testing_data'])))
                results = {i: r for i, r in zip(testset.ids, test(testset))}
                save_test_results(results, method_name, methods_dir,
                                  matlab=matlab)
    finally:
        TempDirectory.delete_all()
