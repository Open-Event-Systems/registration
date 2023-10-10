"""Logic evaluation."""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Tuple

from cattrs import Converter
from oes.template import Context, ValueOrEvaluable, evaluate

if TYPE_CHECKING:
    from oes.interview.logic import Whenable, WhenCondition


def evaluate_whenable(whenable: Whenable, context: Context) -> bool:
    """Evaluate the conditions of a :class:`Whenable`."""
    conditions = (
        whenable.when
        if isinstance(whenable.when, Sequence) and not isinstance(whenable.when, str)
        else (whenable.when,)
    )

    return all(evaluate(c, context) for c in conditions)


def structure_evaluable_or_sequence(converter: Converter, v: object) -> WhenCondition:
    """Structure a single expression or sequence of expressions."""
    if isinstance(v, Sequence) and not isinstance(v, str):
        return converter.structure(v, Tuple[ValueOrEvaluable, ...])  # type: ignore
    else:
        return converter.structure(v, ValueOrEvaluable)  # type: ignore
