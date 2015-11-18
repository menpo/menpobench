from functools import partial
from pathlib import Path
import shutil
import menpobench
from menpobench.cache import (retrieve_results, upload_results, can_upload,
                              hash_of_id)
from menpobench.config import resolve_cache_dir
from menpobench.exception import (CachedExperimentNotAvailable,
                                  MenpoCDNCredentialsMissingError,
                                  OutputDirExistsError)
from menpobench.experiment import retrieve_experiment
from menpobench.method.matlab.base import resolve_matlab_bin_path
from menpobench.output import (save_test_results, compute_and_save_errors,
                               plot_ceds)
from menpobench.utils import centre_str, TempDirectory, norm_path, save_yaml


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


def invoke_train_and_test(training_f, train, testing_f):
    test = invoke_train(train, training_f)
    return invoke_test(test, testing_f)


def invoke_benchmark(experiment_name, output_dir=None, overwrite=False,
                     matlab=False, upload=False, force=False,
                     force_upload=False):
    print('')
    print(centre_str('- - - -  M E N P O B E N C H  - - - -'))
    if upload:
        if not can_upload():
            raise MenpoCDNCredentialsMissingError(
                'MENPO_CDN_S3_ACCESS_KEY and MENPO_CDN_S3_SECRECT_KEY both are'
                ' needed to upload cached results')
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
                raise OutputDirExistsError(
                    "Output directory {} already exists.\n"
                    "Pass '--overwrite' if you want menpobench to delete this "
                    "directory automatically.".format(output_dir))
            else:
                print('--overwrite passed and output directory {} exists - '
                      'deleting\n'.format(output_dir))
                shutil.rmtree(str(output_dir))
        output_dir.mkdir()
        errors_dir = output_dir / 'errors'
        results_dir = output_dir / 'results'
        errors_dir.mkdir()
        results_dir.mkdir()
        results_trainable_dir = results_dir / 'trainable_methods'
        results_untrainable_dir = results_dir / 'untrainable_methods'
        errors_trainable_dir = errors_dir / 'trainable_methods'
        errors_untrainable_dir = errors_dir / 'untrainable_methods'
        save_yaml(ex.config, str(output_dir / 'experiment.yaml'))

    run = partial(run_method, ex, upload=upload, force=force,
                  force_upload=force_upload, matlab=matlab,
                  output=(output_dir is not None))
    try:
        if ex.n_trainable_methods > 0:
            print(centre_str('I. TRAINABLE METHODS'))
            if output_dir is not None:
                results_trainable_dir.mkdir()
                errors_trainable_dir.mkdir()
            else:
                results_trainable_dir = None
                errors_trainable_dir = None

            for i, train in enumerate(ex.trainable_methods, 1):
                print(centre_str('{}/{} - {}'.format(i, ex.n_trainable_methods,
                                                     train), c='='))
                run(train, trainable=True,
                    errors_dir=errors_trainable_dir,
                    results_dir=results_trainable_dir)

        if ex.n_untrainable_methods > 0:
            print(centre_str('II. UNTRAINABLE METHODS', c=' '))
            if output_dir is not None:
                results_untrainable_dir.mkdir()
                errors_untrainable_dir.mkdir()
            else:
                results_untrainable_dir = None
                errors_untrainable_dir = None

            for i, test in enumerate(ex.untrainable_methods, 1):
                print(centre_str('{}/{} - '
                                 '{}'.format(i, ex.n_untrainable_methods,
                                             test), c='='))
                run(test, trainable=False,
                    errors_dir=errors_untrainable_dir,
                    results_dir=results_untrainable_dir)

        # We now have all the results computed - draw the CED curves.
        if output_dir is not None:
            plot_ceds(output_dir)
    finally:
        TempDirectory.delete_all()


# Runs a single method in an experiment.
def run_method(ex, method, trainable=True, upload=False, force=False,
               force_upload=False, output=False, errors_dir=None,
               results_dir=None, matlab=False):
    id_f = ex.trainable_id if trainable else ex.untrainable_id
    run = (partial(invoke_train_and_test, ex.training) if trainable
           else invoke_test)
    cachable = ex.testing.predefined and method.predefined
    if trainable:
        # to cache a trainable method we also need the experiment training
        # to be predefined
        cachable = cachable and ex.training.predefined

    if not force:
        if cachable:
            id_ = id_f(method)
            id_hash = hash_of_id(id_)[:5]
            print(centre_str('[ cache id: {} ]'.format(id_hash)))
            if force_upload and upload:
                results = run(method, ex.testing)
                print('Uploading results for {} (forced)'.format(id_hash))
                upload_results(results, id_)
            else:
                try:
                    results = retrieve_results(id_)
                except CachedExperimentNotAvailable:
                    print('No cached version of {}.'.format(id_hash))
                    results = run(method, ex.testing)
                    if upload:
                        print('Uploading results for {}'.format(id_hash))
                        upload_results(results, id_)
                else:
                    if upload:
                        print('Skipping upload of {} - already '
                              'saved'.format(id_hash))
        elif not output:
            print('Warning: cannot upload {} as it is'
                  'uncachable'.format(method))
        else:
            results = run(method, ex.testing)
    else:
        results = run(method, ex.testing)

    if output:
        save_test_results(results, method.name, results_dir, matlab=matlab)
        compute_and_save_errors(results, ex.error_metrics, method.name,
                                errors_dir)
        print("Results saved for '{}'.\n".format(method))
