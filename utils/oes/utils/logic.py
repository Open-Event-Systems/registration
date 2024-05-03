"""Template logic module."""

from abc import abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any, Callable, Protocol, TypeAlias, runtime_checkable

from attrs import frozen
from cattrs import Converter
from oes.utils.template import Expression, TemplateContext

__all__ = [
    "Evaluable",
    "ValueOrEvaluable",
    "WhenCondition",
    "LogicAnd",
    "LogicOr",
    "evaluate",
    "make_value_or_evaluable_structure_fn",
    "make_when_condition_structure_fn",
    "make_logic_unstructure_fn",
]


@runtime_checkable
class Evaluable(Protocol):
    """An evaluable object."""

    @abstractmethod
    def evaluate(self, context: TemplateContext, /) -> Any:
        """Evaluate the object."""
        ...


ValueOrEvaluable: TypeAlias = Evaluable | object
WhenCondition: TypeAlias = ValueOrEvaluable | Sequence[ValueOrEvaluable]


@frozen
class LogicAnd:
    """Logic AND."""

    and_: Sequence[ValueOrEvaluable] = ()

    def evaluate(self, context: TemplateContext) -> bool:
        """Evaluate the expression."""
        return all(evaluate(item, context) for item in self.and_)


@frozen
class LogicOr:
    """Logic OR."""

    or_: Sequence[ValueOrEvaluable] = ()

    def evaluate(self, context: TemplateContext) -> bool:
        return any(evaluate(item, context) for item in self.or_)


def evaluate(evaluable: Any, context: TemplateContext) -> Any:
    """Evaluate an evaluable."""
    if isinstance(evaluable, Evaluable):
        return evaluable.evaluate(context)
    else:
        return evaluable


def make_value_or_evaluable_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], ValueOrEvaluable]:
    """Make a function to structure a value or evaluable."""

    def structure(v: Any, t: Any) -> ValueOrEvaluable:
        return _structure_value_or_evaluable(converter, v)

    return structure


def make_when_condition_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], WhenCondition]:
    """Make a function to structure a value or evaluable or a sequence of such."""

    def structure(v: Any, t: Any) -> ValueOrEvaluable | Sequence[ValueOrEvaluable]:
        if isinstance(v, Sequence) and not isinstance(v, str):
            items = converter.structure(v, tuple[ValueOrEvaluable, ...])
            return LogicAnd(items)
        else:
            return _structure_value_or_evaluable(converter, v)

    return structure


def _structure_value_or_evaluable(c: Converter, v: Any) -> ValueOrEvaluable:
    if isinstance(v, Mapping) and "and" in v:
        return _structure_and(c, v)
    elif isinstance(v, Mapping) and "or" in v:
        return _structure_or(c, v)
    elif isinstance(v, str):
        return c.structure(v, Expression)
    else:
        return v


def _structure_and(converter: Converter, v: Mapping[str, Any]) -> LogicAnd:
    and_ = v.get("and", ())
    items = converter.structure(and_, tuple[ValueOrEvaluable, ...])
    return LogicAnd(items)


def make_logic_unstructure_fn(
    converter: Converter,
) -> Callable[[LogicAnd | LogicOr], dict]:
    """Make a function to unstructure a logic expression."""

    def unstructure(v: LogicAnd | LogicOr) -> dict:
        if isinstance(v, LogicAnd):
            return {"and": converter.unstructure(v.and_)}
        else:
            return {"or": converter.unstructure(v.or_)}

    return unstructure


def _structure_or(converter: Converter, v: Mapping[str, Any]) -> LogicOr:
    or_ = v.get("or", ())
    items = converter.structure(or_, tuple[ValueOrEvaluable, ...])
    return LogicOr(items)
