"""``attrs`` docs handler."""
from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Set,
)
from typing import Any, Literal, Type, TypeVar, Union, get_args, get_origin

import orjson
from attrs import Attribute, fields
from blacksheep import HTTPException, Request
from blacksheep.server.bindings import BodyBinder, BoundValue, InvalidRequestBody
from blacksheep.server.openapi.v3 import FieldInfo, ObjectTypeHandler, OpenAPIHandler
from cattrs import BaseValidationError, Converter
from cattrs.preconf.orjson import make_converter
from oes.util import is_attrs_class
from openapidocs.v3 import Schema, ValueType

_T = TypeVar("_T")


class AttrsTypeHandler(ObjectTypeHandler):
    """Handler for OpenAPI schemas for ``attrs`` classes."""

    def __init__(self, docs: OpenAPIHandler):
        self._docs = docs

    def handles_type(self, object_type: Any) -> bool:
        return is_attrs_class(object_type)

    def get_type_fields(self, object_type: Any) -> list[FieldInfo]:
        info_list = []

        attr: Attribute
        for attr in fields(object_type):
            info_list.append(
                FieldInfo(name=attr.name, type=_get_field_type(self._docs, attr.type))
            )

        return info_list


class FromAttrs(BoundValue[_T]):
    """Attrs body value."""


class AttrsBinder(BodyBinder):
    """Attrs body binder."""

    handle = FromAttrs
    cattrs_converter: Converter = make_converter()

    @property
    def content_type(self) -> str:
        return "application/json"

    def matches_content_type(self, request: Request) -> bool:
        return request.declares_json()

    async def read_data(self, request: Request) -> Any:
        body = await request.read()

        if body:
            try:
                return orjson.loads(body)
            except ValueError:
                raise InvalidRequestBody
        else:
            return None

    def parse_value(self, data: dict) -> Any:
        try:
            return self.cattrs_converter.structure(data, self.expected_type)
        except BaseValidationError:
            raise HTTPException(422, "Invalid request body")


def _get_field_type(
    docs: OpenAPIHandler, t: object, nullable: bool = False
) -> Union[Schema, Type]:
    """Get a type or :class:`Schema` for the given type."""
    if _is_sequence(t):
        return _get_schema_for_sequence(docs, t, nullable)
    elif _is_mapping(t):
        return _get_schema_for_mapping(docs, t, nullable)
    elif _is_literal(t):
        return _get_schema_for_literal(docs, t, nullable)
    elif _is_union(t):
        return _get_schema_for_union(docs, t)
    elif is_attrs_class(t):
        return _get_schema_for_attrs_class(docs, t, nullable)
    else:
        return docs.get_schema_by_type(t, root_optional=nullable)


def _get_schema_for_union(docs: OpenAPIHandler, t: object) -> Schema:
    args = get_args(t)

    nullable = type(None) in args
    non_null_args = tuple(a for a in args if a is not type(None))  # noqa: E721

    if len(args) == 2 and nullable:
        opt_t = non_null_args[0]
        return _get_field_type(docs, opt_t, nullable)  # noqa: NEW100
    else:
        schemas = [_get_field_type(docs, a) for a in non_null_args]  # noqa: NEW100
        return Schema(one_of=schemas, nullable=nullable)


def _get_schema_for_sequence(docs: OpenAPIHandler, t: object, nullable: bool) -> Schema:
    args = get_args(t)
    # TODO: does not handle heterogeneous tuples
    return Schema(
        type=ValueType.ARRAY,
        items=_get_field_type(docs, args[0]),
        nullable=nullable,
    )


def _get_schema_for_mapping(docs: OpenAPIHandler, t: object, nullable: bool) -> Schema:
    # doesn't seem to be a way to support this...
    return Schema(type=ValueType.OBJECT, nullable=nullable)


def _get_schema_for_literal(docs: OpenAPIHandler, t: object, nullable: bool) -> Schema:
    args = get_args(t)
    return Schema(
        enum=[str(s) for s in args],
        nullable=nullable,
    )


def _get_schema_for_attrs_class(docs: OpenAPIHandler, t: Any, nullable: bool) -> Schema:
    return Schema(
        type=ValueType.OBJECT,
        properties={a.name: _get_field_type(docs, a.type) for a in fields(t)},
        nullable=nullable,
        required=[a.name for a in fields(t) if not _is_optional(a.type)],
    )


def _is_optional(t: object) -> bool:
    origin = get_origin(t)
    args = get_args(t)

    return origin is Union and type(None) in args


def _is_union(t: object) -> bool:
    return get_origin(t) is Union


def _is_optional_union(t: object) -> bool:
    origin = get_origin(t)
    args = get_args(t)

    return origin is Union and len(args) == 2 and type(None) in args


def _is_sequence(t: object) -> bool:
    origin = get_origin(t)
    args = get_args(t)
    return origin in (
        Sequence,
        MutableSequence,
        list,
        tuple,
        set,
        frozenset,
        Set,
        MutableSet,
    ) and (len(args) == 1 or len(args) == 2 and args[1] is Ellipsis)


def _is_mapping(t: object) -> bool:
    origin = get_origin(t)
    return origin in (
        Mapping,
        MutableMapping,
        dict,
    )


def _is_literal(t: object) -> bool:
    return get_origin(t) == Literal
