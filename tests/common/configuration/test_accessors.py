import datetime  # noqa: 251
from typing import Any
import pytest

import data_load_tool
from data_load_tool.common import json
from data_load_tool.common.configuration.exceptions import ConfigFieldMissingException

from data_load_tool.common.configuration.providers import (
    EnvironProvider,
    ConfigTomlProvider,
    SecretsTomlProvider,
)
from data_load_tool.common.configuration.providers.toml import (
    CONFIG_TOML,
    SECRETS_TOML,
    CustomLoaderDocProvider,
)
from data_load_tool.common.configuration.resolve import resolve_configuration
from data_load_tool.common.configuration.specs import (
    GcpServiceAccountCredentialsWithoutDefaults,
    ConnectionStringCredentials,
)
from data_load_tool.common.configuration.specs.config_providers_context import ConfigProvidersContainer
from data_load_tool.common.configuration.utils import get_resolved_traces, ResolvedValueTrace
from data_load_tool.common.runners.configuration import PoolRunnerConfiguration
from data_load_tool.common.typing import AnyType, ConfigValue, SecretValue, TSecretValue


from tests.utils import preserve_environ
from tests.common.configuration.utils import environment, toml_providers

RESOLVED_TRACES = get_resolved_traces()


def test_accessor_singletons() -> None:
    assert data_load_tool.config.value is ConfigValue
    assert data_load_tool.secrets.value is SecretValue


def test_getter_accessor(toml_providers: ConfigProvidersContainer, environment: Any) -> None:
    with pytest.raises(KeyError) as py_ex:
        data_load_tool.config["_unknown"]
    with pytest.raises(ConfigFieldMissingException) as py_ex:
        data_load_tool.config["_unknown"]
    assert py_ex.value.fields == ["_unknown"]

    with pytest.raises(ConfigFieldMissingException) as py_ex:
        data_load_tool.secrets["_unknown"]
    assert py_ex.value.fields == ["_unknown"]

    environment["VALUE"] = "{SET"
    assert data_load_tool.config["value"] == "{SET"
    assert RESOLVED_TRACES[".value"] == ResolvedValueTrace(
        "value", "{SET", None, AnyType, [], EnvironProvider().name, None
    )
    assert data_load_tool.secrets["value"] == "{SET"
    assert RESOLVED_TRACES[".value"] == ResolvedValueTrace(
        "value", "{SET", None, TSecretValue, [], EnvironProvider().name, None
    )

    # get sectioned values
    assert data_load_tool.config["typecheck.str_val"] == "test string"
    assert RESOLVED_TRACES["typecheck.str_val"] == ResolvedValueTrace(
        "str_val", "test string", None, AnyType, ["typecheck"], CONFIG_TOML, None
    )

    environment["DLT__THIS__VALUE"] = "embedded"
    assert data_load_tool.config["data_load_tool.this.value"] == "embedded"
    assert RESOLVED_TRACES["data_load_tool.this.value"] == ResolvedValueTrace(
        "value", "embedded", None, AnyType, ["data_load_tool", "this"], EnvironProvider().name, None
    )
    assert data_load_tool.secrets["data_load_tool.this.value"] == "embedded"
    assert RESOLVED_TRACES["data_load_tool.this.value"] == ResolvedValueTrace(
        "value", "embedded", None, TSecretValue, ["data_load_tool", "this"], EnvironProvider().name, None
    )


def test_getter_auto_cast(toml_providers: ConfigProvidersContainer, environment: Any) -> None:
    environment["VALUE"] = "{SET}"
    assert data_load_tool.config["value"] == "{SET}"
    # bool
    environment["VALUE"] = "true"
    assert data_load_tool.config["value"] is True
    environment["VALUE"] = "False"
    assert data_load_tool.config["value"] is False
    environment["VALUE"] = "yes"
    assert data_load_tool.config["value"] == "yes"
    # int
    environment["VALUE"] = "17261"
    assert data_load_tool.config["value"] == 17261
    environment["VALUE"] = "-17261"
    assert data_load_tool.config["value"] == -17261
    # float
    environment["VALUE"] = "17261.4"
    assert data_load_tool.config["value"] == 17261.4
    environment["VALUE"] = "-10e45"
    assert data_load_tool.config["value"] == -10e45
    # list
    environment["VALUE"] = "[1,2,3]"
    assert data_load_tool.config["value"] == [1, 2, 3]
    assert data_load_tool.config["value"][2] == 3
    # dict
    environment["VALUE"] = '{"a": 1}'
    assert data_load_tool.config["value"] == {"a": 1}
    assert data_load_tool.config["value"]["a"] == 1
    # if not dict or list then original string must be returned, null is a JSON -> None
    environment["VALUE"] = "null"
    assert data_load_tool.config["value"] == "null"

    # typed values are returned as they are
    assert isinstance(data_load_tool.config["typecheck.date_val"], datetime.datetime)

    # access dict from toml
    services_json_dict = data_load_tool.secrets["destination.bigquery"]
    assert (
        data_load_tool.secrets["destination.bigquery"]["client_email"]
        == "loader@a7513.iam.gserviceaccount.com"
    )
    assert RESOLVED_TRACES["destination.bigquery"] == ResolvedValueTrace(
        "bigquery",
        services_json_dict,
        None,
        TSecretValue,
        ["destination"],
        SECRETS_TOML,
        None,
    )
    # equivalent
    assert (
        data_load_tool.secrets["destination.bigquery.client_email"] == "loader@a7513.iam.gserviceaccount.com"
    )
    assert RESOLVED_TRACES["destination.bigquery.client_email"] == ResolvedValueTrace(
        "client_email",
        "loader@a7513.iam.gserviceaccount.com",
        None,
        TSecretValue,
        ["destination", "bigquery"],
        SECRETS_TOML,
        None,
    )


def test_getter_accessor_typed(toml_providers: ConfigProvidersContainer, environment: Any) -> None:
    # get a dict as str
    credentials_str = '{"secret_value":"2137","project_id":"mock-project-id-credentials"}'
    # the typed version coerces the value into desired type, in this case "dict" -> "str"
    assert data_load_tool.secrets.get("credentials", str) == credentials_str
    # note that trace keeps original value of "credentials" which was of dictionary type
    assert RESOLVED_TRACES[".credentials"] == ResolvedValueTrace(
        "credentials", json.loads(credentials_str), None, str, [], SECRETS_TOML, None
    )
    # unchanged type
    assert isinstance(data_load_tool.secrets.get("credentials"), dict)
    # fail on type coercion
    environment["VALUE"] = "a"
    with pytest.raises(ValueError):
        data_load_tool.config.get("value", int)
    # not found -> return none
    assert data_load_tool.config.get("_unk") is None
    # credentials string will be parsed using specified type
    credentials_str = "databricks+connector://token:<databricks_token>@<databricks_host>:443/<database_or_schema_name>?conn_timeout=15&search_path=a,b,c"
    c = data_load_tool.secrets.get("databricks.credentials", ConnectionStringCredentials)
    # as before: the value in trace is the value coming from the provider (as is)
    assert RESOLVED_TRACES["databricks.credentials"] == ResolvedValueTrace(
        "credentials", credentials_str, None, ConnectionStringCredentials, ["databricks"], SECRETS_TOML, ConnectionStringCredentials  # type: ignore[arg-type]
    )
    assert c.drivername == "databricks+connector"
    c2 = data_load_tool.secrets.get("destination.credentials", GcpServiceAccountCredentialsWithoutDefaults)
    assert c2.client_email == "loader@a7513.iam.gserviceaccount.com"


def test_setter(toml_providers: ConfigProvidersContainer, environment: Any) -> None:
    assert data_load_tool.secrets.writable_provider.name == "secrets.toml"
    assert data_load_tool.config.writable_provider.name == "config.toml"

    data_load_tool.config["new_key"] = "new_value"
    assert data_load_tool.config["new_key"] == "new_value"
    # not visible through secrets now (config.toml not included)
    with pytest.raises(KeyError):
        assert data_load_tool.secrets["new_key"] == "new_value"

    data_load_tool.secrets["new_secret"] = TSecretValue("a_secret")
    assert data_load_tool.secrets["new_secret"] == "a_secret"
    # now visible (config is in secrets)
    assert data_load_tool.config["new_secret"] == "a_secret"

    # add sections
    data_load_tool.secrets["pipeline.new.credentials"] = {"api_key": "skjo87a7nnAAaa"}
    assert data_load_tool.secrets["pipeline.new.credentials"] == {"api_key": "skjo87a7nnAAaa"}
    # check the toml directly
    assert data_load_tool.secrets.writable_provider._config_doc["pipeline"]["new"]["credentials"] == {"api_key": "skjo87a7nnAAaa"}  # type: ignore[attr-defined]

    # mod the config and use it to resolve the configuration
    data_load_tool.config["pool"] = {"pool_type": "process", "workers": 21}
    c = resolve_configuration(PoolRunnerConfiguration(), sections=("pool",))
    assert dict(c) == {
        "pool_type": "process",
        "start_method": None,
        "workers": 21,
        "run_sleep": 0.1,
    }


def test_secrets_separation(toml_providers: ConfigProvidersContainer) -> None:
    # secrets are available both in config and secrets
    assert data_load_tool.config.get("credentials") is not None
    assert data_load_tool.secrets.get("credentials") is not None

    # configs are not available in secrets
    assert data_load_tool.config.get("api_type") is not None
    assert data_load_tool.secrets.get("api_type") is None


def test_access_injection(toml_providers: ConfigProvidersContainer) -> None:
    @data_load_tool.source
    def the_source(
        api_type=data_load_tool.config.value,
        credentials: GcpServiceAccountCredentialsWithoutDefaults = data_load_tool.secrets.value,
        databricks_creds: ConnectionStringCredentials = data_load_tool.secrets.value,
    ):
        assert api_type == "REST"
        assert credentials.client_email == "loader@a7513.iam.gserviceaccount.com"
        assert databricks_creds.drivername == "databricks+connector"
        return data_load_tool.resource([1, 2, 3], name="data")

    # inject first argument, the rest pass explicitly
    the_source(
        credentials=data_load_tool.secrets["destination.credentials"],
        databricks_creds=data_load_tool.secrets["databricks.credentials"],
    )


def test_provider_registration(toml_providers: ConfigProvidersContainer) -> None:
    toml_providers.providers.clear()

    def loader():
        return {"api_url": "https://example.com/api"}

    @data_load_tool.source
    def test_source(api_url=data_load_tool.config.value):
        assert api_url == "https://example.com/api"
        return data_load_tool.resource([1, 2, 3], name="data")

    provider = CustomLoaderDocProvider("mock", loader, False)
    assert provider.supports_secrets is False

    with pytest.raises(ConfigFieldMissingException):
        test_source()

    # now register
    data_load_tool.config.register_provider(provider)
    test_source()
