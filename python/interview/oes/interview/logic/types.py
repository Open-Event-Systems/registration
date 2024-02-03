"""Logic types."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, Sequence, TypeVar, Union

from oes.template import Context, Evaluable, ValueOrEvaluable
from typing_extensions import TypeAlias

WhenCondition: TypeAlias = Union[Sequence[ValueOrEvaluable], ValueOrEvaluable]
"""A ``when`` condition."""

_T = TypeVar("_T", covariant=True)

_K = TypeVar("_K")
_V = TypeVar("_V", covariant=True)


class _Protocol(Protocol[_T]):
    """No-op generic protocol to work around a cattrs bug.

    References:
        https://github.com/python-attrs/cattrs/issues/374
    """

    pass


class Whenable(_Protocol[Any], Protocol):
    """An object with a ``when`` condition."""

    @property
    def when(self) -> WhenCondition:
        """The ``when`` condition."""
        return ()


class ValuePointer(Evaluable, Protocol):
    """A pointer to a value in a document."""

    @abstractmethod
    def evaluate(self, context: Context) -> object:
        """Evaluate the pointer with the given context."""
        ...

    @abstractmethod
    def set(self, context: Context, value: object) -> Context:
        """Set the value this object points to in the given context."""
        ...
