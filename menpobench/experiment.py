import pyrx
from menpobench import predefined_dir
from menpobench.utils import load_yaml


def predefined_experiment_dir():
    return predefined_dir() / 'experiment'


def predefined_experiment_path(name):
    return predefined_experiment_dir() / '{}.yaml'.format(name)


def list_predefined_experiments():
    return sorted([p.stem for p in predefined_experiment_dir().glob('*.yaml')])


def load_experiment(experiment_name):
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
    return config


SCHEMA = None


def _load_schema():
    global SCHEMA
    rx = pyrx.Factory({"register_core_types": True})
    s = load_yaml(predefined_dir() / 'schema.yaml')
    SCHEMA = rx.make_schema(s)


def experiment_is_valid(config):
    if SCHEMA is None:
        _load_schema()
    return SCHEMA.check(config)
