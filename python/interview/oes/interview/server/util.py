"""Attrs utils."""

from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import Any, Type, TypeVar

import orjson
from blacksheep import Content, Request, Response
from blacksheep.server.bindings import BoundValue, InvalidRequestBody, JSONBinder
from cattrs import BaseValidationError, Converter

_T = TypeVar("_T")

_request_ctx: ContextVar[dict[str, Any]] = ContextVar("_request_ctx", default={})


async def request_context_middleware(
    request: Request, handler: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to provide a context ``dict`` for each request."""
    token = _request_ctx.set({})
    try:
        return await handler(request)
    finally:
        _request_ctx.reset(token)


def get_request_context() -> dict[str, Any]:
    """Get the current request context."""
    return _request_ctx.get()


def json_response(v: object, /, *, status: int = 200) -> Response:
    """JSON response function."""
    ctx = get_request_context()
    converter: Converter = ctx["converter"]
    data = converter.unstructure(v)
    bytes_ = orjson.dumps(data)
    return Response(status, content=Content(b"application/json", bytes_))


class FromAttrs(BoundValue[_T]):
    """Parse the body value from an attrs class."""

    pass


# TODO: move to util


class AttrsBinder(JSONBinder):
    """Attrs binder."""

    handle = FromAttrs

    def get_default_binder_for_body(self, expected_type: Type):
        def converter(data):
            ctx = get_request_context()
            converter: Converter = ctx["converter"]
            try:
                return converter.structure(data, expected_type)
            except BaseValidationError as e:
                raise InvalidRequestBody() from e

        return converter
