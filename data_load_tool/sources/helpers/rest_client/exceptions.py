from data_load_tool.common.exceptions import DltException


class RESTClientException(DltException):
    pass


class IgnoreResponseException(RESTClientException):
    pass


class PaginatorSetupError(RESTClientException, ValueError):
    pass


class PaginatorNotFound(RESTClientException):
    pass
