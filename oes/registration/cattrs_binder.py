"""Attrs binder."""

from collections.abc import Callable
from typing import Any, Generic, Type, TypeVar
from blacksheep import Request
from blacksheep.exceptions import HTTPException, BadRequest
from blacksheep.server.bindings import (
    Binder,
    BodyBinder,
    BoundValue,
    JSONBinder,
    MissingBodyError,
)
from cattrs import BaseValidationError, Converter
import orjson

_T = TypeVar("_T")


class CattrsBodyError(Exception):
    """Raised when cattrs body parsing fails."""

    pass


class FromCattrs(BoundValue[_T]):
    """A bound body value from cattrs."""

    pass


class CattrsBinder(Binder, Generic[_T]):
    """Cattrs binder."""

    handle = FromCattrs
    cattrs_converter: Converter = Converter()

    def __init__(
        self,
        expected_type: Type[_T],
        name: str = "body",
        implicit: bool = False,
        required: bool = False,
    ):
        super().__init__(
            expected_type, name, implicit, required, self._cattrs_converter
        )

    async def get_value(self, request: Request) -> _T | None:
        value = await self._get_value(request)
        if value is None and self.required:
            raise MissingBodyError()
        return value

    async def _get_value(self, request: Request) -> _T | None:
        data = await request.read()
        if not data:
            return None
        try:
            json = orjson.loads(data)
        except ValueError:
            raise BadRequest("Invalid JSON")
        assert self.converter
        return self.converter(json)

    def _cattrs_converter(self, obj: Any) -> Any:
        try:
            return self.cattrs_converter.structure(obj, self.expected_type)
        except BaseValidationError as exc:
            raise CattrsBodyError(f"Invalid body: {repr(exc)}")
