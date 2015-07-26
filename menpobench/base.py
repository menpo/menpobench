from pathlib import Path
import menpobench
import shutil
from menpobench.config import resolve_cache_dir
from menpobench.experiment import retrieve_experiment
from menpobench.output import save_test_results, save_errors, plot_ceds
from menpobench.utils import centre_str, TempDirectory, norm_path, save_yaml


def invoke_benchmark(experiment_name, output_dir, overwrite=False,
                     matlab=False):
    print('')
    print(centre_str('- - - -  M E N P O B E N C H  - - - -'))
    print(centre_str('v' + menpobench.__version__))
    print(centre_str('config: {}'.format(experiment_name)))
    print(centre_str('output: {}'.format(output_dir)))
    print(centre_str('cache: {}'.format(resolve_cache_dir())))
    print('')
    # Load the experiment and check it's schematically valid
    ex = retrieve_experiment(experiment_name)
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
        if ex.has_methods:
            print(centre_str('I. TRAINABLE METHODS'))
            results_methods_dir.mkdir()
            errors_methods_dir.mkdir()

            for i, m in enumerate(ex.methods, 1):

                # Retrieval
                train, method_name = m
                print(centre_str('{}/{} - {}'.format(i, ex.n_methods,
                                                     method_name), c='='))

                # A. Training
                print(centre_str('training', c='-'))
                print("Training '{}' with {}".format(method_name, ex.training))
                test = train(ex.training())
                print("Training of '{}' completed.".format(method_name))

                # B. Testing
                print(centre_str('testing', c='-'))
                print("Testing '{}' with {}".format(method_name, ex.testing))
                test_set = ex.testing()
                results = test(test_set)

                # C. Save results
                results_dict = {i: r for i, r in zip(test_set.ids, results)}
                save_test_results(results_dict, method_name,
                                  results_methods_dir, matlab=matlab)
                save_errors(test_set.gt_shapes, results,
                            ex.error_metrics, method_name,
                            errors_methods_dir)
                print("Testing of '{}' completed.\n".format(method_name))

        if ex.has_untrainable_methods:
            print(centre_str('II. UNTRAINABLE METHODS', c=' '))
            n_untrainable_methods = len(ex.untrainable_methods)
            results_untrainable_dir.mkdir()
            errors_untrainable_dir.mkdir()

            for i, m in enumerate(ex.untrainable_methods, 1):

                # Retrieval
                test, method_name = m
                print(centre_str('{}/{} - {}'.format(i,
                                                     ex.n_untrainable_methods,
                                                     method_name), c='='))

                # A. Testing
                print(centre_str('testing', c='-'))
                test_set = ex.load_testing_data()
                print("Testing '{}' with {}".format(method_name, test_set))
                results = test(test_set.generator)

                # B. Save results
                results_dict = {i: r for i, r in zip(test_set.generator.ids,
                                                     results)}
                save_test_results(results_dict, method_name,
                                  results_untrainable_dir, matlab=matlab)
                save_errors(test_set.generator.gt_shapes, results,
                            ex.error_metrics, method_name,
                            errors_untrainable_dir)
                print("Testing of '{}' completed.".format(method_name))

        # We now have all the results computed - draw the CED curves.
        plot_ceds(output_dir)
    finally:
        TempDirectory.delete_all()
