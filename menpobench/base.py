from menpobench.dataset import retrieve_datasets
from menpobench.method import retrieve_method
from menpobench.utils import norm_path
import yaml


def invoke_benchmark(yaml_path):
    r"""
    Invoke a benchmark specified in a yaml file.
    """

    with open(norm_path(yaml_path), 'rt') as f:
        c = yaml.load(f)

    for m in c['methods']:
        trainer = retrieve_method(m)
        training_generator = retrieve_datasets(c['training_data'])
        method = trainer(training_generator)
        testing_generator = retrieve_datasets(c['testing_data'])
        results = method(testing_generator)

    for m in c['untrainable_methods']:
        method = retreive_untrainable_method(m)
        training_generator = retrieve_datasets(c['training_data'])
        method = trainer(training_generator)
        testing_generator = retrieve_datasets(c['testing_data'])
        results = method(testing_generator)