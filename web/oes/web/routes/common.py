"""Common utils."""

from oes.utils.response import ResponseConverter
from sanic.exceptions import HTTPException

response_converter = ResponseConverter()


class Conflict(HTTPException):
    """Conflict error."""

    status_code = 409
    quiet = True
