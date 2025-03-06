import pytest

from data_load_tool.common.configuration import resolve_configuration
from data_load_tool.common.schema import Schema
from data_load_tool.common.storages import SchemaStorageConfiguration, SchemaStorage


from tests.utils import autouse_test_storage, preserve_environ


@pytest.fixture
def schema() -> Schema:
    return Schema("event")


@pytest.fixture
def schema_storage() -> SchemaStorage:
    C = resolve_configuration(
        SchemaStorageConfiguration(),
        explicit_value={
            "import_schema_path": "tests/common/cases/schemas/rasa",
            "external_schema_format": "json",
        },
    )
    return SchemaStorage(C, makedirs=True)
