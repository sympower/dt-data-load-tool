from typing import Any
import data_load_tool


@data_load_tool.source
def ethereum() -> Any:
    # this just tests if the schema "ethereum" was loaded
    return data_load_tool.resource([1, 2, 3], name="data")
