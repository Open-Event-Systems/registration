"""Logic objects."""
from __future__ import annotations

import typing
from collections.abc import Mapping, Sequence
from typing import Any, Tuple, Union

from attrs import frozen
from typing_extensions import TYPE_CHECKING

from oes.template.expression import Expression
from oes.template.types import Context, Evaluable, ValueOrEvaluable

if TYPE_CHECKING:
    from cattrs import Converter


@frozen
class LogicAnd(Evaluable):
    """Logic AND."""

    and_: Sequence[ValueOrEvaluable] = ()
    """The expressions."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the expression."""
        return all(evaluate(c, context) for c in self.and_)


@frozen
class LogicOr(Evaluable):
    """Logic OR."""

    or_: Sequence[ValueOrEvaluable] = ()
    """The expressions."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the expression."""
        return any(evaluate(c, context) for c in self.or_)


@frozen
class LogicNot(Evaluable):
    """Logic NOT."""

    not_: ValueOrEvaluable
    """The expression."""

    def evaluate(self, context: Context) -> Any:
        """Evaluate the expression."""
        return not evaluate(self.not_, context)


def evaluate(obj: object, context: Context) -> object:
    """Evaluate an evaluable or value."""
    if isinstance(obj, Evaluable):
        return obj.evaluate(context)
    else:
        return obj


def structure_value_or_evaluable(
    c: Converter, v: object, t: object
) -> ValueOrEvaluable:
    """Structure an evaluable or value."""
    if isinstance(v, str):
        return c.structure(v, Expression)
    elif (
        isinstance(v, Mapping)
        and len(v) == 1
        and ("and" in v or "or" in v or "not" in v)
    ):
        return structure_logic(c, v, t)
    else:
        return v


def structure_logic(c: Converter, v: object, t: object) -> Evaluable:
    """Structure a logic object."""
    if isinstance(v, Mapping) and len(v) == 1:
        if "and" in v:
            exprs = c.structure(v["and"], Tuple[ValueOrEvaluable, ...])
            return LogicAnd(exprs)
        elif "or" in v:
            exprs = c.structure(v["or"], Tuple[ValueOrEvaluable, ...])
            return LogicOr(exprs)
        elif "not" in v:
            expr = c.structure(v["not_"], ValueOrEvaluable)
            return LogicNot(expr)

    raise ValueError(f"Invalid logic expression: {v}")


def unstructure_logic(
    converter: Converter, v: Union[LogicAnd, LogicOr, LogicNot]
) -> dict[str, object]:
    """Unstructure a logic object."""
    if isinstance(v, LogicAnd):
        return {"and": converter.unstructure(v.and_)}
    elif isinstance(v, LogicOr):
        return {"or": converter.unstructure(v.or_)}
    elif isinstance(v, LogicNot):
        return {"not": converter.unstructure(v.not_)}
    else:
        typing.assert_never(v)
