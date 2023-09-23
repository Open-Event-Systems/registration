"""Response helpers."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, Optional, TypeVar

import orjson
from blacksheep import Content, HTTPException, Response
from blacksheep.exceptions import NotFound


class Conflict(HTTPException):
    """HTTP 409."""

    def __init__(self, message: str = "Conflict"):
        super().__init__(409, message)


class PreconditionFailed(HTTPException):
    """HTTP 412."""

    def __init__(self, message: str = "Precondition Failed"):
        super().__init__(412, message)


class PreconditionRequired(HTTPException):
    """HTTP 428."""

    def __init__(self, message: str = "Precondition Required"):
        super().__init__(428, message)


class JSONResponseFunc:
    """Callable to create a JSON response."""

    def __init__(self, default: Optional[Callable[[Any], Any]] = None):
        """Create a JSON response func.

        Args:
            default: A JSON ``default`` callable.
        """
        self._default = default

    def __call__(
        self,
        obj: object,
        /,
        *,
        status_code: int = 200,
        headers: Optional[Iterable[tuple[bytes, bytes]]] = None,
    ) -> Response:
        """Return a JSON response."""
        return Response(
            status_code,
            list(headers) if headers is not None else None,
            Content(
                b"application/json",
                orjson.dumps(obj, default=self._default),
            ),
        )


_T = TypeVar("_T")


def check_404(obj: Optional[_T], /) -> _T:
    """Raise :class:`NotFound` if the given object is ``None``."""
    if obj is None:
        raise NotFound
    return obj
