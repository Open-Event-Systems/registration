"""Logic objects."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, TypeAlias

from attrs import frozen
from oes.template.expression import Expression
from oes.template.types import Context, Evaluable, ValueOrEvaluable
from typing_extensions import assert_never

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


LogicObject: TypeAlias = LogicAnd | LogicOr | LogicNot
"""A logic object."""

LogicObjectTypes = (LogicAnd, LogicOr, LogicNot)
"""The logic object types."""


def evaluate(obj: object, context: Context) -> Any:
    """Evaluate an evaluable or value."""
    if isinstance(obj, Evaluable):
        return obj.evaluate(context)
    else:
        return obj


def make_value_or_evaluable_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], ValueOrEvaluable]:
    """Get a function to structure a value or evaluable."""

    def structure(v: Any, t: Any) -> ValueOrEvaluable:
        if isinstance(v, str):
            return converter.structure(v, Expression)
        elif (
            isinstance(v, Mapping)
            and len(v) == 1
            and ("and" in v or "or" in v or "not" in v)
        ):
            print("structure", v)
            return converter.structure(v, LogicObject)  # type: ignore
        else:
            return v

    return structure


def make_logic_structure_fn(converter: Converter) -> Callable[[Any, Any], LogicObject]:
    """Get a function to structure a logic object."""

    def structure(v: Any, t: Any) -> LogicObject:
        if isinstance(v, Mapping) and len(v) == 1:
            if "and" in v:
                exprs = converter.structure(v["and"], tuple[ValueOrEvaluable, ...])
                return LogicAnd(exprs)
            elif "or" in v:
                exprs = converter.structure(v["or"], tuple[ValueOrEvaluable, ...])
                return LogicOr(exprs)
            elif "not" in v:
                expr = converter.structure(
                    v["not"],
                    ValueOrEvaluable,  # type: ignore
                )
                return LogicNot(expr)
        raise ValueError(f"Invalid logic expression: {v}")

    return structure


def make_logic_unstructure_fn(
    converter: Converter,
) -> Callable[[LogicObject], dict[str, Any]]:
    """Get a function to unstructure a logic object."""

    def unstructure(v: LogicObject) -> dict[str, Any]:
        if isinstance(v, LogicAnd):
            return {"and": converter.unstructure(v.and_)}
        elif isinstance(v, LogicOr):
            return {"or": converter.unstructure(v.or_)}
        elif isinstance(v, LogicNot):
            return {"not": converter.unstructure(v.not_)}
        else:
            assert_never(v)

    return unstructure
