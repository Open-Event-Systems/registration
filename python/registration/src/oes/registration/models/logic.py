"""Logic module."""
from abc import abstractmethod
from typing import Any, Protocol, Sequence, TypeVar, Union

from oes.template import Context, ValueOrEvaluable, evaluate
from typing_extensions import TypeAlias

# TODO: move these somewhere else?

WhenCondition: TypeAlias = Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]]

_T = TypeVar("_T")


class _Protocol(Protocol[_T]):
    """Temporary workaround for a cattrs bug."""

    # TODO: Remove when fixed


class Whenable(_Protocol[Any]):
    """Class with a ``when`` condition."""

    @property
    @abstractmethod
    def when(self) -> WhenCondition:
        """The ``when`` condition."""
        ...


def when_matches(whenable: Whenable, context: Context) -> bool:
    """Return whether the conditions match."""
    if isinstance(whenable.when, Sequence) and not isinstance(whenable.when, str):
        return all(evaluate(expr, context) for expr in whenable.when)
    else:
        return bool(evaluate(whenable.when, context))
