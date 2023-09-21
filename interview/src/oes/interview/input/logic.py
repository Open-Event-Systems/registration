"""Logic module."""
from collections.abc import Sequence
from typing import Tuple, Union

from cattrs import Converter
from oes.interview.input.types import Whenable
from oes.template import Context, ValueOrEvaluable, evaluate


def evaluate_whenable(whenable: Whenable, context: Context) -> bool:
    """Evaluate the conditions of a :class:`Whenable`."""
    conditions = (
        whenable.when
        if isinstance(whenable.when, Sequence) and not isinstance(whenable.when, str)
        else (whenable.when,)
    )

    return all(evaluate(c, context) for c in conditions)


def structure_evaluable_or_sequence(
    converter: Converter, v: object, t: object
) -> Union[Sequence[ValueOrEvaluable], ValueOrEvaluable]:
    """Structure a single expression or sequence of expressions."""
    if isinstance(v, Sequence) and not isinstance(v, str):
        return converter.structure(v, Tuple[ValueOrEvaluable, ...])
    else:
        return converter.structure(v, ValueOrEvaluable)
