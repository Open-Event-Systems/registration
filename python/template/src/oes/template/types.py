"""Base types."""
from abc import abstractmethod
from collections.abc import Mapping
from typing import Any, Union

from typing_extensions import Protocol, TypeAlias, runtime_checkable

Context: TypeAlias = Mapping[str, Any]
"""Template/expression context"""


@runtime_checkable
class Evaluable(Protocol):
    """Evaluable object."""

    @abstractmethod
    def evaluate(self, context: Context) -> Any:
        """Evaluate this evaluable."""
        ...


ValueOrEvaluable: TypeAlias = Union[Evaluable, object]
"""A value or evaluable type."""
