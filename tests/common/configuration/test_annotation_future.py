from __future__ import annotations

from typing import Optional

from data_load_tool.common.configuration import configspec
from data_load_tool.common.configuration.resolve import resolve_configuration
from data_load_tool.common.configuration.specs import BaseConfiguration

from tests.utils import preserve_environ
from tests.common.configuration.utils import environment


def test_str_annotations(environment) -> None:
    @configspec
    class DataConf(BaseConfiguration):
        x: int = None
        x_7: Optional[int] = 3

    assert DataConf.__annotations__ == {"x": "int", "x_7": "Optional[int]"}
    assert DataConf.get_resolvable_fields() == {"x": int, "x_7": Optional[int]}

    # resolve it
    environment["X"] = "10"
    c = resolve_configuration(DataConf())
    assert c.x == 10
