from typing import Any, Iterator

import data_load_tool

from data_load_tool.common import json
from data_load_tool.common.configuration.specs import BaseConfiguration
from data_load_tool.common.runners import Venv
from data_load_tool.common.runners.stdout import iter_stdout
from data_load_tool.common.typing import DictStrAny


# create a standalone resource from a pipe to another process stdout. deselect the source by default as it will be used mostly as a data source to a transformer
@data_load_tool.resource(selected=False, spec=BaseConfiguration)
def json_stdout(venv: Venv, command: str, *script_args: Any) -> Iterator[DictStrAny]:
    """Create a standalone resource from a pipe to another process stdout. Yields line by line. Parses lines as json."""
    # use pipe iterator and mapping function to get dict iterator from pipe
    yield from map(lambda s: json.loads(s), iter_stdout(venv, command, *script_args))  # type: ignore
