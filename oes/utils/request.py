"""Request utils."""

from typing import Type, TypeVar

import orjson
from cattrs import BaseValidationError, Converter
from loguru import logger
from sanic import BadRequest, NotFound, Request, SanicException

__all__ = [
    "CattrsBody",
    "raise_not_found",
]

_T = TypeVar("_T")


class CattrsBody:
    """Cattrs body reader."""

    def __init__(self, request: Request, converter: Converter):
        self.request = request
        self.converter = converter

    async def __call__(self, structure_as: Type[_T]) -> _T:
        """Read and structure the body."""
        if not self.request.body:
            raise BadRequest
        try:
            json = orjson.loads(self.request.body)
        except ValueError:
            raise BadRequest
        try:
            return self.converter.structure(json, structure_as)
        except BaseValidationError as exc:
            logger.opt(exception=exc).debug(f"Invalid body: {exc}")
            raise SanicException("Invalid body", status_code=422) from exc


def raise_not_found(obj: _T | None) -> _T:
    """Raise :class:`NotFound` if the object is ``None``."""
    if obj is None:
        raise NotFound
    return obj
