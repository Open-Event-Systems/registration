"""Base types."""

from abc import abstractmethod
from collections.abc import Mapping
from typing import Any, Protocol, TypeAlias, runtime_checkable

Context: TypeAlias = Mapping[str, Any]
"""Template/expression context"""


@runtime_checkable
class Evaluable(Protocol):
    """Evaluable object."""

    @abstractmethod
    def evaluate(self, context: Context) -> Any:
        """Evaluate this evaluable."""
        ...


ValueOrEvaluable: TypeAlias = Evaluable | object
"""A value or evaluable type."""
