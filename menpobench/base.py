from pathlib import Path
import menpobench
import shutil
from menpobench.config import resolve_cache_dir
from menpobench.experiment import retrieve_experiment
from menpobench.output import save_test_results, save_errors, plot_ceds
from menpobench.utils import centre_str, TempDirectory, norm_path, save_yaml
from menpobench.method.matlab.base import resolve_matlab_bin_path
from menpobench.cache import retrieve_cached_run
from menpobench.exception import CachedExperimentNotAvailable


def invoke_train(train, training_f):
    print(centre_str('training', c='-'))
    print("Training '{}' with {}".format(train, training_f))
    train_set = training_f()
    test = train(train_set)
    print("Training of '{}' completed.".format(train))
    return test

def invoke_test(test, testing_f):
    print(centre_str('testing', c='-'))
    print("Testing '{}' with {}".format(test, testing_f))
    test_set = testing_f()
    results = test(test_set)
    print("Testing of '{}' completed.\n".format(test))
    return results, test_set

def invoke_train_and_test(train, training_f, testing_f):
    test = invoke_train(train, training_f)
    return invoke_test(test, testing_f)


def save_results(results, test_set, method, error_metrics):
    # C. Save results
    results_dict = {i: r for i, r in zip(test_set.ids, results)}
    save_test_results(results_dict, method.name,
                      results_methods_dir, matlab=matlab)
    save_errors(test_set.gt_shapes, results, error_metrics,
                method.name, errors_methods_dir)
    print("Results saved for '{}'.\n".format(method))


def invoke_benchmark(experiment_name, output_dir, overwrite=False,
                     matlab=False):
    print('')
    print(centre_str('- - - -  M E N P O B E N C H  - - - -'))
    print(centre_str('v' + menpobench.__version__))
    print(centre_str('config: {}'.format(experiment_name)))
    print(centre_str('output: {}'.format(output_dir)))
    print(centre_str('cache: {}'.format(resolve_cache_dir())))

    # Load the experiment and check it's schematically valid
    ex = retrieve_experiment(experiment_name)

    # Check if we have any dependency on matlab
    if ex.depends_on_matlab:
        print(centre_str('matlab: {}'.format(resolve_matlab_bin_path())))

    print('')
    # Handle the creation of the output directory
    output_dir = Path(norm_path(output_dir))
    if output_dir.is_dir():
        if not overwrite:
            raise ValueError("Output directory {} already exists.\n"
                             "Pass '--overwrite' if you want menpobench to "
                             "delete this directory "
                             "automatically.".format(output_dir))
        else:
            print('--overwrite passed and output directory {} exists - '
                  'deleting\n'.format(output_dir))
            shutil.rmtree(str(output_dir))
    output_dir.mkdir()
    errors_dir = output_dir / 'errors'
    results_dir = output_dir / 'results'
    errors_dir.mkdir()
    results_dir.mkdir()
    results_methods_dir = results_dir / 'methods'
    results_untrainable_dir = results_dir / 'untrainable_methods'
    errors_methods_dir = errors_dir / 'methods'
    errors_untrainable_dir = errors_dir / 'untrainable_methods'
    save_yaml(ex.config, str(output_dir / 'experiment.yaml'))
    # Loop over all requested methods, training and testing them.
    # Note that methods are, by definition trainable.
    try:
        if ex.n_trainable_methods > 0:
            print(centre_str('I. TRAINABLE METHODS'))
            results_methods_dir.mkdir()
            errors_methods_dir.mkdir()

            for i, train in enumerate(ex.trainable_methods, 1):

                # Retrieval
                print(centre_str('{}/{} - {}'.format(i, ex.n_trainable_methods,
                                                     train), c='='))

                if (ex.training.predefined and ex.testing.predefined and
                    train.predefined):
                    print('checking hash')
                    try:
                        results = retrieve_cached_run(
                            ex.trainable_method_id(train))
                    except CachedExperimentNotAvailable:
                        print('no cached version available. Training anyway')
                        results, test_set = invoke_train_and_test(train,
                                                                  ex.training,
                                                                  ex.testing)
                else:
                    results, test_set = invoke_train_and_test(train,
                                                              ex.training,
                                                              ex.testing)
                    # C. Save results
                    results_dict = {i: r for i, r in zip(test_set.ids, results)}
                save_test_results(results_dict, train.name,
                                  results_methods_dir, matlab=matlab)
                save_errors(test_set.gt_shapes, results, ex.error_metrics,
                            train.name, errors_methods_dir)
                print("Results saved for '{}'.\n".format(train))

        if ex.n_untrainable_methods > 0:
            print(centre_str('II. UNTRAINABLE METHODS', c=' '))
            results_untrainable_dir.mkdir()
            errors_untrainable_dir.mkdir()

            for i, test in enumerate(ex.untrainable_methods, 1):

                # Retrieval
                print(centre_str('{}/{} - {}'.format(i,
                                                     ex.n_untrainable_methods,
                                                     test), c='='))

                # A. Testing
                print(centre_str('testing', c='-'))

                if (ex.testing.predefined and test.predefined):
                    print('testing, and method predefined - checking hash')
                    print(ex.untrainable_method_id(test))

                test_set = ex.load_testing_data()
                print("Testing '{}' with {}".format(test, test_set))
                results = test(test_set)

                # B. Save results
                results_dict = {i: r for i, r in zip(test_set.generator.ids,
                                                     results)}
                save_test_results(results_dict, test.name,
                                  results_untrainable_dir, matlab=matlab)
                save_errors(test_set.gt_shapes, results, ex.error_metrics,
                            test.name, errors_untrainable_dir)
                print("Testing of '{}' completed.".format(test))

        # We now have all the results computed - draw the CED curves.
        plot_ceds(output_dir)
    finally:
        TempDirectory.delete_all()
