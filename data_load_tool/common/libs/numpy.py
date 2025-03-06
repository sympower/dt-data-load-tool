from data_load_tool.common.exceptions import MissingDependencyException

try:
    import numpy
except ModuleNotFoundError:
    raise MissingDependencyException("data_load_tool Numpy Helpers", ["numpy"])
