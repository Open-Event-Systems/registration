"""Input types."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias

from oes.utils.template import TemplateContext

if TYPE_CHECKING:
    from oes.interview.input.field import Field


JSONSchema: TypeAlias = Mapping[str, Any]
"""The JSON schema type."""

Validator: TypeAlias = Callable[[Any], Any]


class FieldTemplate(Protocol):
    """A field template."""

    @property
    @abstractmethod
    def python_type(self) -> type:
        """The Python type of the field's value."""
        ...

    @property
    @abstractmethod
    def type(self) -> str:
        """The field type."""
        ...

    @abstractmethod
    def get_field(self, context: TemplateContext) -> Field:
        """Get a :class:`Field` from this template."""
        ...
