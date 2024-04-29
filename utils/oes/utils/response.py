"""HTTP response utilities."""

import functools
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, ParamSpec, Type, overload

from cattrs.preconf.orjson import OrjsonConverter, make_converter
from sanic import HTTPResponse

__all__ = [
    "ResponseConverter",
]

_P = ParamSpec("_P")


class ResponseConverter:
    """A tool to convert handler return values into HTTP responses."""

    converter: OrjsonConverter
    """The :class:`Converter` used."""

    def __init__(self):
        self.converter = make_converter()

    @overload
    def __call__(self, unstructure_as: Type | None = None, /) -> Callable[
        [Callable[_P, Awaitable[Any]]],
        Callable[_P, Coroutine[None, None, HTTPResponse]],
    ]: ...

    @overload
    def __call__(
        self, handler: Callable[_P, Awaitable[Any]], /
    ) -> Callable[_P, Coroutine[None, None, HTTPResponse]]: ...

    def __call__(self, arg=None) -> Any:
        """Decorate a handler to unstructure the return value into a response."""
        if callable(arg) and not isinstance(arg, type):
            unstructure_as = None
            func = arg
        else:
            unstructure_as = arg
            func = None

        def decorator(handler):
            @functools.wraps(handler)
            async def wrapper(*a, **kw):
                resp = await handler(*a, **kw)
                return self.make_response(resp, unstructure_as)

            return wrapper

        return decorator(func) if func is not None else decorator

    def make_response(
        self, value: Any, unstructure_as: Type | None = None
    ) -> HTTPResponse:
        """Make a response from the value."""
        body = self.converter.dumps(value, unstructure_as)
        return HTTPResponse(body, content_type="application/json")
