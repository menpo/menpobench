# We can't find a MenpoBench module (Python file)
class ModuleNotFoundError(Exception):
    pass


# There is no cached experiment file for this experiment
class CachedExperimentNotAvailable(Exception):
    pass


# A schema-level error - e.g. a missing/mistyped key in a YAML file.
class SchemaError(Exception):

    def __init__(self, name, type, report):
        self.type_ = type
        self.name = name
        self.report = report

    def __str__(self):
        return "The schema for {} {} is invalid:\n{}".format(self.type_,
                                                             self.name,
                                                             self.report)


# No metadata object defined in a module where we expect it to be.
class MissingMetadataError(Exception):

    def __init__(self, type):
        self.type_ = type

    def __str__(self):
        return "The metadata dict for {} is missing".format(self.type_)


# A piece of config we need is absent from the user config.
class MissingConfigKeyError(KeyError):
    pass
