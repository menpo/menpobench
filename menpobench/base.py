from pathlib import Path
import menpobench
import shutil
from menpobench.config import resolve_cache_dir
from menpobench.dataset import retrieve_datasets
from menpobench.errormetric import retrieve_error_metrics
from menpobench.experiment import load_experiment, experiment_schema
from menpobench.method import retrieve_method, retrieve_untrainable_method
from menpobench.output import save_test_results, save_errors, plot_ceds
from menpobench.utils import centre_str, TempDirectory, norm_path, save_yaml
from menpobench.schema import schema_error_report, schema_is_valid, SchemaError


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
    s = experiment_schema()
    c = load_experiment(experiment_name)
    if not schema_is_valid(s, c):
        report = schema_error_report(s, c)
        raise SchemaError(experiment_name, "experiment", report)
    # prepare the error metrics
    error_metrics = retrieve_error_metrics(c['error_metric'])
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
    save_yaml(c, str(output_dir / 'experiment.yaml'))
    # Loop over all requested methods, training and testing them.
    # Note that methods are, by definition trainable.
    try:
        if 'methods' in c:
            print(centre_str('I. TRAINABLE METHODS'))
            n_methods = len(c['methods'])
            results_methods_dir.mkdir()
            errors_methods_dir.mkdir()

            for i, m in enumerate(c['methods'], 1):

                # Retrieval
                train, method_name = retrieve_method(m)
                print(centre_str('{}/{} - {}'.format(i, n_methods, method_name)
                                 , c='='))

                # A. Training
                print(centre_str('training', c='-'))
                train_set = retrieve_datasets(c['training_data'])
                print("Training '{}' with {}".format(method_name, train_set))
                test = train(train_set.generator)
                print("Training of '{}' completed.".format(method_name))

                # B. Testing
                print(centre_str('testing', c='-'))
                test_set = retrieve_datasets(c['testing_data'], test=True)
                print("Testing '{}' with {}".format(method_name, test_set))
                results = test(test_set.generator)

                # C. Save results
                results_dict = {i: r for i, r in zip(test_set.generator.ids,
                                                     results)}
                save_test_results(results_dict, method_name,
                                  results_methods_dir, matlab=matlab)
                save_errors(test_set.generator.gt_shapes, results,
                            error_metrics, method_name, errors_methods_dir)
                print("Testing of '{}' completed.\n".format(method_name))

        if 'untrainable_methods' in c:
            print(centre_str('II. UNTRAINABLE METHODS', c=' '))
            n_untrainable_methods = len(c['untrainable_methods'])
            results_untrainable_dir.mkdir()
            errors_untrainable_dir.mkdir()

            for i, m in enumerate(c['untrainable_methods'], 1):

                # Retrieval
                test, method_name = retrieve_untrainable_method(m)
                print(centre_str('{}/{} - {}'.format(i, n_untrainable_methods,
                                                     method_name), c='='))

                # A. Testing
                print(centre_str('testing', c='-'))
                test_set = retrieve_datasets(c['testing_data'], test=True)
                print("Testing '{}' with {}".format(method_name, test_set))
                results = test(test_set.generator)

                # B. Save results
                results_dict = {i: r for i, r in zip(test_set.generator.ids,
                                                     results)}
                save_test_results(results_dict, method_name,
                                  results_untrainable_dir, matlab=matlab)
                save_errors(test_set.generator.gt_shapes, results,
                            error_metrics, method_name, errors_untrainable_dir)
                print("Testing of '{}' completed.".format(method_name))

        # We now have all the results computed - draw the CED curves.
        plot_ceds(output_dir)
    finally:
        TempDirectory.delete_all()
