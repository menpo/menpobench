from menpobench import invoke_benchmark, configure_cache_dir
from menpobench.config import NoMenpoBenchConfigError


def invoke_benchmark_from_cli(yaml_path):
    try:
        invoke_benchmark(yaml_path)
    except NoMenpoBenchConfigError:
        print('Welcome to menpobench. To start, you will need to choose a directory')
        print('that menpobench can use as a cache.')
        print('This directory will be managed by menpobench to store datasets and')
        print('temporary results. Anticipate it to get quite large (~20GB).')
        cache_dir = raw_input('Please enter cache directory: ')
        configure_cache_dir(cache_dir)
        # now we have a cache dir, re-run
        invoke_benchmark_from_cli(yaml_path)
    except ValueError as e:
        print('ERROR: {}'.format(e.message))
        exit(1)
