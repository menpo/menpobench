from menpobench import invoke_benchmark, configure_cache_dir
from menpobench.config import NoMenpoBenchConfigError


def invoke_benchmark_from_cli(experiment_name):
    try:
        invoke_benchmark(experiment_name)
    except NoMenpoBenchConfigError:
        print('Welcome to menpobench. To start, you will need to choose a directory')
        print('that menpobench can use as a cache.')
        print('This directory will be managed by menpobench to store datasets and')
        print('temporary results. Anticipate it to get quite large (~20GB).')
        cache_dir = raw_input('Please enter cache directory: ')
        configure_cache_dir(cache_dir)
        # now we have a cache dir, re-run
        invoke_benchmark_from_cli(experiment_name)
    except ValueError as e:
        print('ERROR: {}'.format(e.message))
        exit(1)


def list_all_predefined():
    from menpobench.experiment import list_predefined_experiments
    from menpobench.dataset import list_predefined_datasets
    from menpobench.method import (list_predefined_methods,
                                   list_predefined_untrainable_methods)
    import yaml
    print(yaml.dump({'datasets': list_predefined_datasets(),
                     'methods': list_predefined_methods(),
                     'untrainable_methods': list_predefined_untrainable_methods(),
                     'experiments': list_predefined_experiments()
                     }, default_flow_style=False))
