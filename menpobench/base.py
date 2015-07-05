from menpobench.dataset import retrieve_datasets
from menpobench.method import retrieve_method, retrieve_untrainable_method
from menpobench.utils import load_yaml


def invoke_benchmark(yaml_path):
    r"""
    Invoke a benchmark specified in a yaml file.
    """
    c = load_yaml(yaml_path)

    for m in c['methods']:
        train = retrieve_method(m)
        training_generator = retrieve_datasets(c['training_data'])
        test = train(training_generator)
        testing_generator = retrieve_datasets(c['testing_data'])
        results = test(testing_generator)

    for m in c['untrainable_methods']:
        test = retrieve_untrainable_method(m)
        testing_generator = retrieve_datasets(c['testing_data'])
        results = test(testing_generator)
