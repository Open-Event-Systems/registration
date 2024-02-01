"""Pointer module."""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Union, cast, overload

import pyparsing as pp
from attrs import field, frozen
from oes.interview.logic.types import ValuePointer
from oes.template import Context
from oes.util import make_immutable


class InvalidPointerError(ValueError):
    """Raised when a :class:`ValuePointer` is not valid."""

    pass


@frozen
class PointerSegment(ValuePointer):
    """A single segment of a value pointer."""

    value: object

    def evaluate(self, context: object, /) -> object:
        """Evaluate this segment."""
        return _get(context, self.value)

    def set(self, context: object, value: object, /) -> Context:
        """Set the value this segment points to."""
        return cast(Context, _set(context, self.value, value))

    def __str__(self) -> str:
        if isinstance(self.value, str):
            if re.fullmatch(r"(?![0-9])[a-z0-9_]+", self.value, re.I):
                return f".{self.value}"
            else:
                esc = self.value.replace("\\", "\\\\").replace('"', '\\"')
                return f'["{esc}"]'
        else:
            return f"[{self.value}]"


@frozen
class PointerImpl(ValuePointer, Sequence[PointerSegment]):
    """:class:`ValuePointer` implementation."""

    segments: Sequence[PointerSegment] = field(default=(), converter=lambda v: tuple(v))

    @overload
    def __getitem__(self, index: int) -> PointerSegment:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[PointerSegment]:
        ...

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[PointerSegment, Sequence[PointerSegment]]:
        if isinstance(index, slice):
            new_segments = self.segments[index]
            return PointerImpl(new_segments)
        else:
            return self.segments[index]

    def __len__(self):
        return len(self.segments)

    def evaluate(self, context: object, /) -> object:
        cur = context
        for segment in self.segments:
            cur = segment.evaluate(cur)
        return cur

    def set(self, context: object, value: object, /) -> Context:
        value = make_immutable(value)
        return cast(Context, _set_recursive(context, self.segments, value))

    def __str__(self) -> str:
        if len(self) > 0:
            return str(self.segments[0].value) + "".join(
                str(s) for s in self.segments[1:]
            )
        else:
            return "Pointer(())"


def _get(context: object, key: object) -> object:
    if isinstance(key, str):
        return _get_obj(context, key)
    elif isinstance(key, int) and not isinstance(key, bool):
        return _get_arr(context, key)
    else:
        raise TypeError(f"Invalid index: {key}")


def _get_arr(context: object, key: int) -> object:
    if not isinstance(context, Sequence) or isinstance(context, str):
        raise TypeError(f"Not an array: {context}")
    return context[key]


def _get_obj(context: object, key: str) -> object:
    if not isinstance(context, Mapping):
        raise TypeError(f"Not an object: {context}")
    return context[key]


def _set_recursive(
    context: object, segments: Sequence[PointerSegment], value: object
) -> object:
    if len(segments) == 1:
        return segments[0].set(context, value)
    else:
        next_ = segments[0].evaluate(context)
        next_ = _set_recursive(next_, segments[1:], value)
        return segments[0].set(context, next_)


def _set(context: object, key: object, value: object) -> object:
    if isinstance(key, str):
        return _set_obj(context, key, value)
    elif isinstance(key, int) and not isinstance(key, bool):
        return _set_arr(context, key, value)
    else:
        raise TypeError(f"Invalid index: {key}")


def _set_arr(context: object, key: int, value: object) -> Sequence[object]:
    if not isinstance(context, Sequence) or isinstance(context, str):
        raise TypeError(f"Not an array: {context}")
    return *context[:key], value, *context[key + 1 :]


def _set_obj(context: object, key: str, value: object) -> Mapping[object, object]:
    if not isinstance(context, Mapping):
        raise TypeError(f"Not an object: {context}")
    return make_immutable({**context, key: value})


class _Parsing:
    space = pp.White(" \t")[...].suppress()

    number = pp.Regex(r"(?:[1-9][0-9]*|0(?![0-9]))")

    @number.set_parse_action
    @staticmethod
    def _parse_number(res):
        return int(res[0])

    string = pp.QuotedString(quote_char='"', esc_char="\\")

    @string.set_parse_action
    @staticmethod
    def _parse_string(res):
        return res[0]

    constant = string | number

    name = pp.Regex(r"(?![0-9])[a-z0-9_]+", re.I)

    @name.set_parse_action
    @staticmethod
    def _parse_name(res):
        return res[0]

    property_access = "." + name

    @property_access.set_parse_action
    @staticmethod
    def _parse_property_access(res):
        return res[1]

    index_access = "[" + space + constant + space + "]"

    @index_access.set_parse_action
    @staticmethod
    def _parse_index_access(res):
        return res[1]

    pointer_segment = property_access | index_access

    @pointer_segment.set_parse_action
    @staticmethod
    def _parse_pointer_segment(res):
        return PointerSegment(res[0])

    pointer = space + (name + pointer_segment[...]).leave_whitespace()

    @pointer.set_parse_action
    @staticmethod
    def _parse_pointer(res):
        return PointerSegment(res[0]), *res[1:]


def parse_pointer(value: str) -> ValuePointer:
    """Parse a value pointer."""
    return parse_pointer_impl(value)


def parse_pointer_impl(value: str) -> PointerImpl:
    """Parse a value pointer."""
    try:
        res = _Parsing.pointer.parse_string(value, parse_all=True)
        return PointerImpl(tuple(res[0]))
    except pp.ParseException as e:
        raise InvalidPointerError(value) from e
