"""Type declarations."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Mapping
from enum import Enum
from typing import Any, Optional, Protocol

from oes.interview.logic import ValuePointer
from oes.template import Context, Expression
from typing_extensions import TypeAlias

UserResponse: TypeAlias = Mapping[str, object]
"""A user response."""

ResponseParser: TypeAlias = Callable[
    [UserResponse, Context], Mapping[ValuePointer, object]
]
"""A callable that parses a response into a mapping of variable locations/values."""

JSONSchema: TypeAlias = Mapping[str, object]
"""The JSON schema type."""


class FieldType(str, Enum):
    """Enum of field type IDs."""

    text = "text"
    number = "number"
    select = "select"
    date = "date"
    button = "button"


class Field(Protocol):
    """A user input field.

    Provides a JSON schema, an :func:`attr.ib` field for parsing/validating the
    input, and where to store the value.
    """

    @abstractmethod
    def get_field_info(self, context: Context) -> Any:
        """The :func:`attr.ib` object for this field."""
        ...

    @abstractmethod
    def get_schema(self, context: Context) -> JSONSchema:
        """Get the JSON schema representing this field.

        Args:
            context: The context for rendering templates.
        """
        ...

    @property
    def optional(self) -> bool:
        """Whether the field is optional."""
        return False

    @property
    @abstractmethod
    def set(self) -> Optional[ValuePointer]:
        """The value pointer to set."""
        ...


class Option(Protocol):
    """A select option."""

    @property
    @abstractmethod
    def id(self) -> Optional[str]:
        """The option ID."""
        ...

    @property
    @abstractmethod
    def value(self) -> Any:
        """The option value."""
        ...

    @property
    def value_expr(self) -> Expression | None:
        """An expression of the option value."""
        return None

    @abstractmethod
    def get_schema(self, context: Context, *, id: Optional[str] = None) -> JSONSchema:
        """Get the JSON schema for this option."""
        ...
