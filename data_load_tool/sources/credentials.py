from data_load_tool.common.configuration.specs import (
    GcpServiceAccountCredentials,
    GcpOAuthCredentials,
    GcpCredentials,
    AwsCredentials,
    AzureCredentials,
)
from data_load_tool.common.configuration.specs import ConnectionStringCredentials
from data_load_tool.common.configuration.specs import OAuth2Credentials
from data_load_tool.common.configuration.specs import CredentialsConfiguration, configspec
from data_load_tool.common.storages.configuration import FileSystemCredentials, FilesystemConfiguration


__all__ = [
    "GcpServiceAccountCredentials",
    "GcpOAuthCredentials",
    "GcpCredentials",
    "AwsCredentials",
    "AzureCredentials",
    "ConnectionStringCredentials",
    "OAuth2Credentials",
    "CredentialsConfiguration",
    "configspec",
    "FileSystemCredentials",
    "FilesystemConfiguration",
]
