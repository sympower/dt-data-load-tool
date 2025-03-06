from data_load_tool.common.exceptions import MissingDependencyException


try:
    from pandas.io.sql import _wrap_result
except ModuleNotFoundError:
    raise MissingDependencyException("data_load_tool pandas helper for sql", ["pandas"])
