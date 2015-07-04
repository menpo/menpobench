from menpobench.dataset import generate_chained_datasets
from menpobench.method import train
from menpobench.utils import norm_path
import yaml


def invoke_benchmark(yaml_path):

    with open(norm_path(yaml_path), 'rt') as f:
        c = yaml.load(f)

    for m in c['methods']:
        trainer = train(m)
        training_generator = generate_chained_datasets(c['training_data'])
        method = trainer(training_generator)
        testing_generator = generate_chained_datasets(c['testing_data'])
        results = method(testing_generator)
