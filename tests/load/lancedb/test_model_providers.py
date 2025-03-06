"""
Test intricacies and configuration related to each provider.
"""

import os
from typing import Iterator, Any, Generator

import pytest
from lancedb import DBConnection  # type: ignore
from lancedb.embeddings import EmbeddingFunctionRegistry  # type: ignore
from lancedb.table import Table  # type: ignore

import data_load_tool
from data_load_tool.common.configuration import resolve_configuration
from data_load_tool.common.typing import DictStrStr
from data_load_tool.common.utils import uniq_id
from data_load_tool.destinations.impl.lancedb import lancedb_adapter
from data_load_tool.destinations.impl.lancedb.configuration import LanceDBClientConfiguration
from data_load_tool.destinations.impl.lancedb.lancedb_client import LanceDBClient
from tests.load.utils import drop_active_pipeline_data, sequence_generator
from tests.pipeline.utils import assert_load_info

# Mark all tests as essential, don't remove.
pytestmark = pytest.mark.essential


@pytest.fixture(autouse=True)
def drop_lancedb_data() -> Iterator[Any]:
    yield
    drop_active_pipeline_data()


def test_lancedb_ollama_endpoint_configuration() -> None:
    os.environ["DESTINATION__LANCEDB__EMBEDDING_MODEL_PROVIDER"] = "ollama"
    os.environ["DESTINATION__LANCEDB__EMBEDDING_MODEL"] = "nomic-embed-text"
    os.environ["DESTINATION__LANCEDB__EMBEDDING_MODEL_PROVIDER_HOST"] = "http://198.163.194.3:24233"

    config = resolve_configuration(
        LanceDBClientConfiguration()._bind_dataset_name(dataset_name="dataset"),
        sections=("destination", "lancedb"),
    )
    assert config.embedding_model_provider == "ollama"
    assert config.embedding_model == "nomic-embed-text"
    assert config.embedding_model_provider_host == "http://198.163.194.3:24233"
