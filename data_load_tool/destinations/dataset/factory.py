from typing import Union

from data_load_tool.common.destination import TDestinationReferenceArg
from data_load_tool.common.destination.dataset import SupportsReadableDataset
from data_load_tool.common.destination.typing import TDatasetType
from data_load_tool.common.schema import Schema

from data_load_tool.destinations.dataset.dataset import ReadableDBAPIDataset


def dataset(
    destination: TDestinationReferenceArg,
    dataset_name: str,
    schema: Union[Schema, str, None] = None,
    dataset_type: TDatasetType = "auto",
) -> SupportsReadableDataset:
    return ReadableDBAPIDataset(destination, dataset_name, schema, dataset_type)
