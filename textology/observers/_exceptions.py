"""Exceptions for input/output requests via observation callbacks."""


class ObserverException(Exception):
    """Base for all observation based exceptions."""


class PreventUpdate(ObserverException):
    """Exception that indicates all updates should be skipped in an observation callback."""


class UnknownObserver(ObserverException):
    """Exception that indicates an observer callback was requested that does not exist or has not been registered."""
