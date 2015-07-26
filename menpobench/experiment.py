from menpobench import predefined_dir
from menpobench.dataset import retrieve_datasets
from menpobench.errormetric import retrieve_error_metrics
from menpobench.exception import SchemaError
from menpobench.method import retrieve_method
from menpobench.schema import schema_error_report, schema_is_valid
from menpobench.utils import load_yaml, load_schema, memoize


def predefined_experiment_dir():
    return predefined_dir() / 'experiment'


def predefined_experiment_path(name):
    return predefined_experiment_dir() / '{}.yaml'.format(name)


def list_predefined_experiments():
    return sorted([p.stem for p in predefined_experiment_dir().glob('*.yaml')])


def retrieve_experiment(experiment_name):
    if experiment_name.endswith('.yml') or experiment_name.endswith('.yaml'):
        # user is giving a path to an experiment file
        try:
            config = load_yaml(experiment_name)
        except IOError:
            raise ValueError("Requested experiment configuration at path '{}' "
                             "does not exist".format(experiment_name))
    else:
        # predefined experiment
        try:
            config = load_yaml(predefined_experiment_path(experiment_name))
        except IOError:
            raise ValueError("Requested predefined experiment configuration "
                             "'{}' does not exist".format(experiment_name))
    return Experiment(config)


class Experiment(object):

    def __init__(self, c):
        # Load the experiment and check it's schematically valid
        s = experiment_schema()
        if not schema_is_valid(s, c):
            report = schema_error_report(s, c)
            raise SchemaError(c, "experiment", report)

        self.config = c

        # prepare the error metrics
        self.error_metrics = retrieve_error_metrics(c['error_metric'])

        if 'training_data' in c:
            self.training = retrieve_datasets(c['training_data'])
        self.testing = retrieve_datasets(c['testing_data'], test=True)

        if 'methods' in c:
            if 'training_data' not in c:
                raise ValueError('Trying to test trainable methods but no '
                                 'training_data was provided')
            self.methods = [retrieve_method(m) for m in c['methods']]

        if 'untrainable_methods' in c:
            self.untrainable_methods = [retrieve_method(m)
                                        for m in c['untrainable_methods']]

    @property
    def has_methods(self):
        return hasattr(self, 'methods')

    @property
    def has_untrainable_methods(self):
        return hasattr(self, 'untrainable_methods')

    @property
    def n_methods(self):
        return len(self.methods) if self.has_methods else 0

    @property
    def n_untrainable_methods(self):
        return (len(self.untrainable_methods)
                if self.has_untrainable_methods else 0)


@memoize
def experiment_schema():
    return load_schema(predefined_dir() / 'experiment_schema.yaml')
