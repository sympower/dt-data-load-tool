from typing import Literal, Optional

from data_load_tool.common.schema.typing import (
    _TTableSchemaBase,
    TWriteDisposition,
    TTableReferenceParam,
)

TDatasetType = Literal["auto", "default", "ibis"]


class PreparedTableSchema(_TTableSchemaBase, total=False):
    """Table schema with all hints prepared to be loaded"""

    write_disposition: TWriteDisposition
    references: Optional[TTableReferenceParam]
    _x_prepared: bool  # needed for the type checker
