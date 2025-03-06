from typing import Optional

from data_load_tool.common.configuration import configspec
from data_load_tool.common.configuration.specs import BaseConfiguration
from data_load_tool.common.typing import TSecretStrValue


@configspec
class DBTCloudConfiguration(BaseConfiguration):
    api_token: TSecretStrValue = ""

    account_id: Optional[str] = None
    job_id: Optional[str] = None
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    run_id: Optional[str] = None

    cause: str = "Triggered via API"
    git_sha: Optional[str] = None
    git_branch: Optional[str] = None
    schema_override: Optional[str] = None
