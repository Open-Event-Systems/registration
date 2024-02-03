"""Value pointer module."""

import re
from typing import Any, cast

import pyparsing as pp
from attrs import frozen
from oes.interview.logic.types import ValuePointer
from oes.template import Context, Evaluable, evaluate
from oes.util import make_immutable


class InvalidPointerError(ValueError):
    """Raised when a :class:`ValuePointer` is not valid."""

    pass


@frozen
class Name:
    name: str

    def evaluate(self, context: Context) -> Any:
        return context[self.name]

    def set(self, context: Context, value: Any) -> Context:
        return make_immutable(context) | {self.name: value}

    def __str__(self) -> str:
        return self.name


@frozen
class PropertyAccess:
    object: ValuePointer
    property: str | Evaluable

    def evaluate(self, context: Context) -> Any:
        prop_val = evaluate(self.property, context)
        obj_val = evaluate(self.object, context)
        return obj_val[prop_val]

    def set(self, context: Context, value: Any) -> Context:
        prop_val = evaluate(self.property, context)
        obj_val = evaluate(self.object, context)
        updated = make_immutable(obj_val) | {prop_val: value}
        return self.object.set(context, updated)

    def __str__(self) -> str:
        if isinstance(self.property, str):
            if re.match(r"^(?![0-9])[a-z0-9_]+$", self.property):
                return f"{self.object}.{self.property}"
            else:
                escaped = self.property.replace("\\", "\\\\").replace('"', '\\"')
                return f'{self.object}["{escaped}"]'
        else:
            return f"{self.object}[{self.property}]"


@frozen
class IndexAccess:
    object: ValuePointer
    index: int | Evaluable

    def evaluate(self, context: Context) -> Any:
        index_val = evaluate(self.index, context)
        obj_val = evaluate(self.object, context)
        return obj_val[index_val]

    def set(self, context: Context, value: Any) -> Context:
        index_val = evaluate(self.index, context)
        obj_val = make_immutable(evaluate(self.object, context))
        updated = obj_val[:index_val] + (value,) + obj_val[index_val + 1 :]
        return self.object.set(context, updated)

    def __str__(self) -> str:
        return f"{self.object}[{self.index}]"


class Parsing:
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

    property_access = pp.Group(
        ("." + name("property")) | ("[" + space + string("property") + space + "]")
    )

    index_access = pp.Group("[" + space + number("index") + space + "]")

    pointer_segment = property_access | index_access

    pointer = (
        space
        + (name("name") + pp.Group(pointer_segment[...])("segments")).leave_whitespace()
    )

    @pointer.set_parse_action
    @staticmethod
    def _parse_pointer(res):
        cur: ValuePointer = Name(res["name"])
        for seg in res["segments"]:
            if "property" in seg:
                cur = PropertyAccess(cur, seg["property"])
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
