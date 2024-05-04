"""Logic types."""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol

from oes.utils.logic import Evaluable
from oes.utils.template import TemplateContext


class ValuePointer(Evaluable, Protocol):
    """A pointer to a value in a document."""

    @abstractmethod
    def set(self, context: TemplateContext, value: object) -> TemplateContext:
        """Set the value this object points to in the given context."""
        ...
