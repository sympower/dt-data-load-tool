from data_load_tool.common.exceptions import MissingDependencyException

# FIXME: Remove this after implementing package installer
try:
    import streamlit
except ModuleNotFoundError:
    raise MissingDependencyException(
        "data_load_tool Streamlit Helpers",
        ["streamlit"],
        "data_load_tool Helpers for Streamlit should be run within a streamlit app.",
    )
