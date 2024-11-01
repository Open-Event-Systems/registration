"""Common utils."""

from attrs import frozen
from oes.utils.response import ResponseConverter
from sanic.exceptions import HTTPException

response_converter = ResponseConverter()


class Conflict(HTTPException):
    """Conflict error."""

    status_code = 409
    quiet = True


@frozen
class InterviewStateRequestBody:
    """Interview state request body."""

    state: str
