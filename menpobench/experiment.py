from menpobench import predefined_dir
from menpobench.utils import load_yaml


def predefined_method_dir():
    return predefined_dir() / 'experiment'


def predefined_method_path(name):
    return predefined_method_dir() / '{}.yaml'.format(name)


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
            config = load_yaml(predefined_method_path(experiment_name))
        except IOError:
            raise ValueError("Requested predefined experiment configuration "
                             "'{}' does not exist".format(experiment_name))
    return config
