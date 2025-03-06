from typing import Any
from data_load_tool.common.exceptions import MissingDependencyException

try:
    import pandas
    from pandas import DataFrame
except ModuleNotFoundError:
    raise MissingDependencyException("data_load_tool Pandas Helpers", ["pandas"])


def pandas_to_arrow(df: pandas.DataFrame, preserve_index: bool = False) -> Any:
    """Converts pandas to arrow or raises an exception if pyarrow is not installed"""
    from data_load_tool.common.libs.pyarrow import pyarrow as pa

    # NOTE: None preserves named indexes but ignores unnamed
    return pa.Table.from_pandas(df, preserve_index=preserve_index)
