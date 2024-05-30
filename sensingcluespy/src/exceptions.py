"""Exceptions for sensingcluespy"""


class SensingCluesException(Exception):
    pass


class SCPermissionDenied(SensingCluesException):
    pass


class SCServiceUnavailable(SensingCluesException):
    pass


class SCClientNotFoundError(SensingCluesException):
    pass
