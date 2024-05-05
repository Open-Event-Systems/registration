"""Value pointer module."""

import re
from collections.abc import Mapping, Sequence
from typing import Any, cast

import pyparsing as pp
from attrs import frozen
from oes.interview.immutable import make_immutable
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import evaluate as evaluate_logic
from oes.utils.template import TemplateContext


class InvalidPointerError(ValueError):
    """Raised when a :class:`ValuePointer` is not valid."""

    pass


@frozen
class Name:
    """Name object."""

    name: str

    def evaluate(self, context: TemplateContext) -> Any:
        return context[self.name]

    def set(self, context: TemplateContext, value: Any) -> TemplateContext:
        return make_immutable(context) | {self.name: value}

    def __str__(self) -> str:
        return self.name


@frozen
class IndexAccess:
    """Index access object."""

    object: ValuePointer
    index: str | int

    def evaluate(self, context: TemplateContext) -> Any:
        index_val = evaluate_logic(self.index, context)
        obj_val = evaluate_logic(self.object, context)
        return obj_val[index_val]

    def set(self, context: TemplateContext, value: Any) -> TemplateContext:
        index_val = evaluate_logic(self.index, context)
        obj_val = make_immutable(evaluate_logic(self.object, context))
        if isinstance(obj_val, Mapping):
            if not isinstance(index_val, str):
                raise ValueError(f"Only string keys are supported, got {index_val!r}")
            updated = make_immutable(obj_val) | {index_val: value}
        else:
            if not isinstance(index_val, int):
                raise ValueError(
                    f"Only integer array indices are supported, got {index_val!r}"
                )
            updated = obj_val[:index_val] + (value,) + obj_val[index_val + 1 :]
        return self.object.set(context, updated)

    def __str__(self) -> str:
        if isinstance(self.index, str):
            if re.match(r"^(?![0-9])[a-z0-9_]+$", self.index):
                return f"{self.object}.{self.index}"
            else:
                escaped = self.index.replace("\\", "\\\\").replace('"', '\\"')
                return f'{self.object}["{escaped}"]'
        else:
            return f"{self.object}[{self.index}]"


class Parsing:
    """Parsing namespace."""

    pointer = pp.Forward()

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

    property_access = pp.Group(("." + name("property")))

    index_access = pp.Group("[" + space + (number | string)("index") + space + "]")

    pointer_segment = property_access | index_access

    pointer <<= (
        space
        + (name("name") + pp.Group(pointer_segment[...])("segments")).leave_whitespace()
    )

    @pointer.set_parse_action
    @staticmethod
    def _parse_pointer(res):
        cur: ValuePointer = Name(res["name"])
        for seg in res["segments"]:
            if "property" in seg:
                cur = IndexAccess(cur, seg["property"])
            elif "index" in seg:
                cur = IndexAccess(cur, seg["index"])
            else:
                raise ValueError(seg)
        return cur


def parse_pointer(ptr: str, /) -> ValuePointer:
    """Parse a pointer."""
    try:
        res = Parsing.pointer.parse_string(ptr, parse_all=True)
        return cast(ValuePointer, res[0])
    except pp.ParseException as e:
        raise InvalidPointerError(ptr) from e


def get_path(ptr: ValuePointer, /) -> Sequence[str | int]:
    """Get the path represented by a pointer."""
    return _get_path(ptr)


def _get_path(ptr: ValuePointer) -> Sequence[str | int]:
    if isinstance(ptr, Name):
        return (ptr.name,)
    elif isinstance(ptr, IndexAccess):
        return (*_get_path(ptr.object), ptr.index)
    else:
        raise TypeError(ptr)
