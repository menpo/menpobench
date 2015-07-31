from pathlib import Path
import menpobench
import shutil
from menpobench.config import resolve_cache_dir
from menpobench.experiment import retrieve_experiment
from menpobench.output import save_test_results, compute_and_save_errors, plot_ceds
from menpobench.utils import centre_str, TempDirectory, norm_path, save_yaml
from menpobench.method.matlab.base import resolve_matlab_bin_path
from menpobench.cache import (retrieve_cached_run, can_upload, upload_results,
                              hash_of_id)
from menpobench.exception import (CachedExperimentNotAvailable,
                                  MenpoCDNCredentialsMissingError)


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
    return {id_: {'gt': gt.points.tolist(),
                  'result': r.tojson()}
            for (id_, r, gt) in zip(test_set.ids, results, test_set.gt_shapes)}

def invoke_train_and_test(train, training_f, testing_f):
    test = invoke_train(train, training_f)
    return invoke_test(test, testing_f)


def save_results(results, test_set, method, error_metrics):
    # C. Save results
    results_dict = {i: r for i, r in zip(test_set.ids, results)}
    save_test_results(results_dict, method.name,
                      results_methods_dir, matlab=matlab)
    compute_and_save_errors(test_set.gt_shapes, results, error_metrics,
                method.name, errors_methods_dir)
    print("Results saved for '{}'.\n".format(method))


def invoke_benchmark(experiment_name, output_dir=None, overwrite=False,
                     matlab=False, upload=False, force=False,
                     force_upload=False):
    print('')
    print(centre_str('- - - -  M E N P O B E N C H  - - - -'))
    if upload:
        if not can_upload():
            raise MenpoCDNCredentialsMissingError('MENPO_CDN_S3_ACCESS_KEY and '
                                                  'MENPO_CDN_S3_SECRECT_KEY both are '
                                                  'needed to upload cached results')
        print(centre_str('** MENPO CDN UPLOAD ENABLED **'))
        if force_upload:
            print(centre_str('** UPLOAD FORCED **'))
    print(centre_str('v' + menpobench.__version__))
    print(centre_str('config: {}'.format(experiment_name)))
    if output_dir is not None:
        print(centre_str('output: {}'.format(output_dir)))
    print(centre_str('cache: {}'.format(resolve_cache_dir())))
    if force:
        print(centre_str('FORCED RECOMPUTATION ENABLED'))

    # Load the experiment and check it's schematically valid
    ex = retrieve_experiment(experiment_name)

    # Check if we have any dependency on matlab
    if ex.depends_on_matlab:
        print(centre_str('matlab: {}'.format(resolve_matlab_bin_path())))

    print('')
    if output_dir is not None:
        # Handle the creation of the output directory
        output_dir = Path(norm_path(output_dir))
        if output_dir.is_dir():
            if not overwrite:
                raise ValueError("Output directory {} already exists.\n"
                                 "Pass '--overwrite' if you want menpobench to"
                                 " delete this directory "
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
            if output_dir is not None:
                results_methods_dir.mkdir()
                errors_methods_dir.mkdir()

            for i, train in enumerate(ex.trainable_methods, 1):
                print(centre_str('{}/{} - {}'.format(i, ex.n_trainable_methods,
                                                     train), c='='))
                if not force:
                    cachable = (ex.training.predefined and
                                ex.testing.predefined and
                                train.predefined)
                    if cachable:
                        id_ = ex.trainable_id(train)
                        id_hash = hash_of_id(id_)[:5]
                        print(centre_str('[ cachable: {} ]'.format(id_hash)))
                        if force_upload and upload:
                            results = invoke_train_and_test(train, ex.training,
                                                            ex.testing)
                            print('Uploading results for {} '
                                  '(forced)'.format(id_hash))
                            upload_results(results, id_)
                        else:
                            try:
                                results = retrieve_cached_run(id_)
                            except CachedExperimentNotAvailable:
                                print('No cached version of '
                                      '{}.'.format(id_hash))
                                results = invoke_train_and_test(train,
                                                                ex.training,
                                                                ex.testing)
                                if upload:
                                    print('Uploading results for '
                                          '{}'.format(id_hash))
                                    upload_results(results, id_)
                            else:
                                if upload:
                                    print('Skipping upload of {} - already '
                                          'saved'.format(id_hash))
                    elif output_dir is not None:
                        raise ValueError('Running upload but encounted an '
                                         'uncachable run')
                    else:
                        results = invoke_train_and_test(train, ex.training,
                                                        ex.testing)
                else:
                    results = invoke_train_and_test(train, ex.training,
                                                    ex.testing)

                if output_dir is not None:
                    save_test_results(results, train.name, results_methods_dir,
                                      matlab=matlab)
                    compute_and_save_errors(results, ex.error_metrics,
                                            train.name, errors_methods_dir)
                    print("Results saved for '{}'.\n".format(train))

        if ex.n_untrainable_methods > 0:
            print(centre_str('II. UNTRAINABLE METHODS', c=' '))
            results_untrainable_dir.mkdir()
            errors_untrainable_dir.mkdir()

            for i, test in enumerate(ex.untrainable_methods, 1):
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
                compute_and_save_errors(test_set.gt_shapes, results, ex.error_metrics,
                            test.name, errors_untrainable_dir)
                print("Testing of '{}' completed.".format(test))

        # We now have all the results computed - draw the CED curves.
        if output_dir is not None:
            plot_ceds(output_dir)
    finally:
        TempDirectory.delete_all()
