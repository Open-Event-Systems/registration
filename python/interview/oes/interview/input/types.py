"""Type declarations."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Mapping
from enum import Enum
from typing import Any, Protocol, Type, TypeVar

from oes.interview.logic import ValuePointer
from oes.template import Context
from typing_extensions import TypeAlias

_T_co = TypeVar("_T_co", covariant=True)

FieldParser: TypeAlias = Callable[[object], _T_co]
"""Callable that parses a user's input for a field."""

UserResponse: TypeAlias = Mapping[str, object]
"""A user response."""

ResponseParser: TypeAlias = Callable[
    [UserResponse, Context], Mapping[ValuePointer, object]
]
"""A callable that parses a response into a mapping of variable locations/values."""

JSONSchema: TypeAlias = Mapping[str, Any]
"""The JSON schema type."""


class FieldType(str, Enum):
    """Enum of field type IDs."""

    text = "text"
    number = "number"
    select = "select"
    date = "date"
    button = "button"


class Field(Protocol[_T_co]):
    """An input field."""

    @property
    @abstractmethod
    def type(self) -> Type[_T_co]:
        """The type of the field's parsed value."""
        ...

    @property
    @abstractmethod
    def set(self) -> ValuePointer | None:
        """The value pointer to set."""
        ...

    @property
    @abstractmethod
    def schema(self) -> JSONSchema:
        """The JSON schema item describing the field."""
        ...

    @abstractmethod
    def __call__(self, value: object, /) -> _T_co:
        """Parse the user input."""
        ...


class Option(Protocol[_T_co]):
    """A select option."""

    @property
    @abstractmethod
    def id(self) -> str | None:
        """The option ID."""
        ...

    @property
    @abstractmethod
    def value(self) -> _T_co:
        """The option value."""
        ...

    @property
    @abstractmethod
    def schema(self) -> JSONSchema:
        """The JSON schema for this option."""
        ...


FieldFactory: TypeAlias = Callable[[Context], Field[_T_co]]
"""Callable to create a :class:`Field`."""
