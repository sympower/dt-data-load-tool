import dataclasses
from typing import Final, Optional, Any, Dict, ClassVar, List

from data_load_tool.common.configuration import configspec
from data_load_tool.common.configuration.specs import ConnectionStringCredentials
from data_load_tool.common.destination.client import DestinationClientDwhWithStagingConfiguration
from data_load_tool.common.typing import TSecretStrValue
from data_load_tool.common.utils import digest128


@configspec(init=False)
class DremioCredentials(ConnectionStringCredentials):
    drivername: str = "grpc"
    username: str = None
    password: TSecretStrValue = None
    host: str = None
    port: Optional[int] = 32010
    database: str = None

    __config_gen_annotations__: ClassVar[List[str]] = ["port"]

    def to_native_credentials(self) -> str:
        from data_load_tool.common.libs.sql_alchemy_compat import URL

        return URL.create(
            drivername=self.drivername, host=self.host, port=self.port
        ).render_as_string(hide_password=False)

    def db_kwargs(self) -> Dict[str, Any]:
        return dict(username=self.username, password=self.password)


@configspec
class DremioClientConfiguration(DestinationClientDwhWithStagingConfiguration):
    destination_type: Final[str] = dataclasses.field(default="dremio", init=False, repr=False, compare=False)  # type: ignore[misc]
    credentials: DremioCredentials = None
    staging_data_source: str = None
    """The name of the staging data source"""

    def fingerprint(self) -> str:
        """Returns a fingerprint of host part of a connection string"""
        if self.credentials and self.credentials.host:
            return digest128(self.credentials.host)
        return ""
