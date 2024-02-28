"""Logic types."""
from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, Sequence, Union

from oes.template import Context, Evaluable, ValueOrEvaluable
from typing_extensions import TypeAlias

WhenCondition: TypeAlias = Union[Sequence[ValueOrEvaluable], ValueOrEvaluable]
"""A ``when`` condition."""


class Whenable(Protocol):
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
