import posixpath
import os
from data_load_tool.common.exceptions import MissingDependencyException

from tests.utils import TEST_STORAGE_ROOT
from utils import parse_toml_file


def destination_instantiation_snippet() -> None:
    # @@@DLT_SNIPPET_START shorthand
    import data_load_tool

    pipeline = data_load_tool.pipeline("pipeline", destination="filesystem")
    # @@@DLT_SNIPPET_END shorthand
    assert pipeline.destination.destination_name == "filesystem"

    # @@@DLT_SNIPPET_START class_type
    import data_load_tool

    pipeline = data_load_tool.pipeline("pipeline", destination="data_load_tool.destinations.filesystem")
    # @@@DLT_SNIPPET_END class_type
    assert pipeline.destination.destination_name == "filesystem"

    # @@@DLT_SNIPPET_START class
    import data_load_tool
    from data_load_tool.destinations import filesystem

    pipeline = data_load_tool.pipeline("pipeline", destination=filesystem)
    # @@@DLT_SNIPPET_END class

    assert pipeline.destination.destination_name == "filesystem"

    # @@@DLT_SNIPPET_START instance
    import data_load_tool

    azure_bucket = filesystem("az://dlt-azure-bucket", destination_name="production_az_bucket")
    pipeline = data_load_tool.pipeline("pipeline", destination=azure_bucket)
    # @@@DLT_SNIPPET_END instance
    assert pipeline.destination.destination_name == "production_az_bucket"

    # @@@DLT_SNIPPET_START config_explicit
    import data_load_tool
    from data_load_tool.destinations import postgres

    # pass full credentials - together with the password (not recommended)
    pipeline = data_load_tool.pipeline(
        "pipeline",
        destination=postgres(credentials="postgresql://loader:loader@localhost:5432/dlt_data"),
    )
    # @@@DLT_SNIPPET_END config_explicit

    # @@@DLT_SNIPPET_START config_partial
    import data_load_tool
    from data_load_tool.destinations import postgres

    # pass credentials without password
    # data_load_tool will retrieve the password from ie. DESTINATION__POSTGRES__CREDENTIALS__PASSWORD
    prod_postgres = postgres(credentials="postgresql://loader@localhost:5432/dlt_data")
    pipeline = data_load_tool.pipeline("pipeline", destination=prod_postgres)
    # @@@DLT_SNIPPET_END config_partial

    os.environ["DESTINATION__POSTGRES__CREDENTIALS__PASSWORD"] = "pwd"
    try:
        assert pipeline.destination_client().config.credentials.password == "pwd"  # type: ignore[attr-defined]
    except MissingDependencyException:
        # not very elegant but I do not want to add psycopg2 to docs dependencies
        pass

    # @@@DLT_SNIPPET_START config_partial_spec
    import data_load_tool
    from data_load_tool.destinations import filesystem
    from data_load_tool.sources.credentials import AzureCredentials

    credentials = AzureCredentials()
    # fill only the account name, leave key to be taken from secrets
    credentials.azure_storage_account_name = "production_storage"
    pipeline = data_load_tool.pipeline(
        "pipeline", destination=filesystem("az://dlt-azure-bucket", credentials=credentials)
    )
    # @@@DLT_SNIPPET_END config_partial_spec

    bucket_url = posixpath.join("file://", os.path.abspath(TEST_STORAGE_ROOT))

    # @@@DLT_SNIPPET_START late_destination_access
    import data_load_tool
    from data_load_tool.destinations import filesystem

    # just declare the destination.
    pipeline = data_load_tool.pipeline("pipeline", destination="filesystem")
    # no destination credentials not config needed to extract
    pipeline.extract(["a", "b", "c"], table_name="letters")
    # same to normalize
    pipeline.normalize()
    # here dependencies dependencies will be imported, secrets pulled and destination accessed
    # we pass bucket_url explicitly and expect credentials passed by config provider
    load_info = pipeline.load(destination=filesystem(bucket_url=bucket_url))
    print(load_info)
    # @@@DLT_SNIPPET_END late_destination_access


def test_toml_snippets() -> None:
    parse_toml_file("./destination-toml.toml")
