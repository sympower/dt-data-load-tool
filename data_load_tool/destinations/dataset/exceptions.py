from data_load_tool.common.exceptions import DltException


class DatasetException(DltException):
    pass


class ReadableRelationHasQueryException(DatasetException):
    def __init__(self, attempted_change: str) -> None:
        msg = (
            "This readable relation was created with a provided sql query. You cannot change"
            f" {attempted_change}. Please change the orignal sql query."
        )
        super().__init__(msg)


class ReadableRelationUnknownColumnException(DatasetException):
    def __init__(self, column_name: str) -> None:
        msg = (
            f"The selected column {column_name} is not known in the data_load_tool schema for this releation."
        )
        super().__init__(msg)
