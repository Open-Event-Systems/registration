"""HTTP response utilities."""

import functools
import types
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

    json_default: Callable[[Any], Any] | None
    """A ``default`` function for the JSON encoder."""

    def __init__(
        self,
        converter: OrjsonConverter | None = None,
        json_default: Callable[[Any], Any] | None = None,
    ):
        self.converter = converter or make_converter()
        self.json_default = json_default

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
        if isinstance(arg, types.FunctionType):
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
        body = self.converter.dumps(value, unstructure_as, default=self.json_default)
        return HTTPResponse(body, content_type="application/json")
