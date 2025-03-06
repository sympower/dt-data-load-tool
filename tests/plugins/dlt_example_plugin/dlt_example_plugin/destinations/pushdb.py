import data_load_tool
from data_load_tool.common.schema import TTableSchema
from data_load_tool.common.typing import TDataItems


@data_load_tool.destination(batch_size=250, name="pushdb")
def push_destination(items: TDataItems, table: TTableSchema) -> None:
    pass
