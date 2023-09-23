"""Interview error module."""

from oes.util import ExceptionDetails, get_exception_details


class InterviewError(ValueError):
    """Raised when there is an issue with the interview configuration."""

    pass


class InvalidStateError(ValueError):
    """Raised when an interview state is not valid."""

    pass


class InvalidInputError(ValueError):
    """Raised when user responses are invalid."""

    details: list[ExceptionDetails]

    def __init__(self, exc: Exception):
        super().__init__(exc)
        self.details = get_exception_details(exc)

    def __str__(self) -> str:
        return str(self.details)
