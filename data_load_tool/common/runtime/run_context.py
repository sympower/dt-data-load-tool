import os
import tempfile
from types import ModuleType
from typing import Any, ClassVar, Dict, List, Optional

from data_load_tool.common import known_env
from data_load_tool.common.configuration import plugins
from data_load_tool.common.configuration.container import Container
from data_load_tool.common.configuration.providers import (
    EnvironProvider,
    SecretsTomlProvider,
    ConfigTomlProvider,
)
from data_load_tool.common.configuration.providers.provider import ConfigProvider
from data_load_tool.common.configuration.specs.pluggable_run_context import (
    SupportsRunContext,
    PluggableRunContext,
)

# data_load_tool settings folder
DOT_DLT = os.environ.get(known_env.DLT_CONFIG_FOLDER, ".data_load_tool")


class RunContext(SupportsRunContext):
    """A default run context used by data_load_tool"""

    CONTEXT_NAME: ClassVar[str] = "data_load_tool"

    def __init__(self, run_dir: Optional[str]):
        self._init_run_dir = run_dir or "."

    @property
    def global_dir(self) -> str:
        return self.data_dir

    @property
    def run_dir(self) -> str:
        """The default run dir is the current working directory but may be overridden by DLT_PROJECT_DIR env variable."""
        return os.environ.get(known_env.DLT_PROJECT_DIR, self._init_run_dir)

    @property
    def local_dir(self) -> str:
        return os.environ.get(known_env.DLT_LOCAL_DIR, self._init_run_dir)

    @property
    def settings_dir(self) -> str:
        """Returns a path to data_load_tool settings directory. If not overridden it resides in current working directory

        The name of the setting folder is '.data_load_tool'. The path is current working directory '.' but may be overridden by DLT_PROJECT_DIR env variable.
        """
        return os.path.join(self.run_dir, DOT_DLT)

    @property
    def data_dir(self) -> str:
        return global_dir()

    def initial_providers(self) -> List[ConfigProvider]:
        providers = [
            EnvironProvider(),
            SecretsTomlProvider(self.settings_dir, self.global_dir),
            ConfigTomlProvider(self.settings_dir, self.global_dir),
        ]
        return providers

    @property
    def module(self) -> Optional[ModuleType]:
        try:
            return self.import_run_dir_module(self.run_dir)
        except ImportError:
            return None

    @property
    def runtime_kwargs(self) -> Dict[str, Any]:
        return None

    def get_data_entity(self, entity: str) -> str:
        return os.path.join(self.data_dir, entity)

    def get_run_entity(self, entity: str) -> str:
        """Default run context assumes that entities are defined in root dir"""
        return self.run_dir

    def get_setting(self, setting_path: str) -> str:
        return os.path.join(self.settings_dir, setting_path)

    def plug(self) -> None:
        pass

    def unplug(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self.__class__.CONTEXT_NAME

    @staticmethod
    def import_run_dir_module(run_dir: str) -> ModuleType:
        """Returns a top Python module of the project (if importable)"""
        import importlib

        # trailing separator will be removed by abspath
        run_dir = os.path.abspath(run_dir)
        base_dir = os.path.basename(run_dir)
        if not base_dir:
            raise ImportError(f"run dir {run_dir} looks like filesystem root")
        m_ = importlib.import_module(base_dir)
        if m_.__file__ and m_.__file__.startswith(run_dir):
            return m_
        else:
            raise ImportError(
                f"run dir {run_dir} does not belong to module {m_.__file__} which seems unrelated."
            )


@plugins.hookspec(firstresult=True)
def plug_run_context(
    run_dir: Optional[str], runtime_kwargs: Optional[Dict[str, Any]]
) -> SupportsRunContext:
    """Spec for plugin hook that returns current run context.

    Args:
        run_dir (str): An initial run directory of the context
        runtime_kwargs: Any additional arguments passed to the context via PluggableRunContext.reload

    Returns:
        SupportsRunContext: A run context implementing SupportsRunContext protocol
    """


@plugins.hookimpl(specname="plug_run_context")
def plug_run_context_impl(
    run_dir: Optional[str], runtime_kwargs: Optional[Dict[str, Any]]
) -> SupportsRunContext:
    return RunContext(run_dir)


def global_dir() -> str:
    """Gets default directory where pipelines' data (working directories) will be stored
    1. if DLT_DATA_DIR is set in env then it is used
    2. in user home directory: ~/.data_load_tool/
    3. if current user is root: in /var/data_load_tool/
    4. if current user does not have a home directory: in /tmp/data_load_tool/
    """
    if known_env.DLT_DATA_DIR in os.environ:
        return os.environ[known_env.DLT_DATA_DIR]

    # geteuid not available on Windows
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        # we are root so use standard /var
        return os.path.join("/var", "data_load_tool")

    home = os.path.expanduser("~")
    if home is None or not is_folder_writable(home):
        # no home dir - use temp
        return os.path.join(tempfile.gettempdir(), "data_load_tool")
    else:
        # if home directory is available use ~/.data_load_tool/pipelines
        return os.path.join(home, DOT_DLT)


def is_folder_writable(path: str) -> bool:
    import tempfile

    try:
        # Ensure the path exists
        if not os.path.exists(path):
            return False
        # Attempt to create a temporary file
        with tempfile.TemporaryFile(dir=path):
            pass
        return True
    except OSError:
        return False


def get_plugin_modules() -> List[str]:
    """Return top level module names of all discovered plugins, including `data_load_tool`.

    If current run context is a top level module it is also included, otherwise empty string.
    """
    from data_load_tool.common.configuration.plugins import PluginContext

    # get current run module
    ctx_module = active().module
    run_module_name = ctx_module.__name__ if ctx_module else ""

    return [run_module_name] + [p for p in Container()[PluginContext].plugin_modules] + ["data_load_tool"]


def active() -> SupportsRunContext:
    """Returns currently active run context"""
    return Container()[PluggableRunContext].context
