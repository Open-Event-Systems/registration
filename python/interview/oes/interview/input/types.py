"""Type declarations."""
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Optional, Protocol, TypeVar, Union

from oes.interview.variables.locator import Locator
from oes.template import Context, ValueOrEvaluable
from typing_extensions import TypeAlias

UserResponse: TypeAlias = Mapping[str, object]
"""A user response."""

ResponseParser: TypeAlias = Callable[[UserResponse], Mapping[Locator, object]]
"""A callable that parses a response into a mapping of variable locations/values."""

JSONSchema: TypeAlias = Mapping[str, object]
"""The JSON schema type."""

_T = TypeVar("_T", covariant=True)


class _Protocol(Protocol[_T]):
    """No-op generic protocol to work around a cattrs bug.

    References:
        https://github.com/python-attrs/cattrs/issues/374
    """

    pass


class Field(_Protocol[Any], Protocol):
    """A user input field.

    Provides a JSON schema, an :func:`attr.ib` field for parsing/validating the
    input, and where to store the value.
    """

    @property
    @abstractmethod
    def field_info(self) -> Any:
        """The :func:`attr.ib` object for this field."""
        ...

    @abstractmethod
    def get_schema(self, context: Context, /) -> JSONSchema:
        """Get the JSON schema representing this field.

        Args:
            context: The context for rendering templates.
        """
        ...

    @property
    @abstractmethod
    def set(self) -> Optional[Locator]:
        """The variable location to set."""
        ...


class Option(_Protocol[Any], Protocol):
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

    def get_schema(
        self, context: Context, /, *, id: Optional[str] = None
    ) -> JSONSchema:
        """Get the JSON schema for this option."""
        if id is None and self.id is None:
            raise ValueError("An ID must be provided")

        schema = {
            "const": id or self.id,
        }
        return schema


class Whenable(_Protocol[Any], Protocol):
    """An object with a ``when`` condition."""

    @property
    def when(self) -> Union[Sequence[ValueOrEvaluable], ValueOrEvaluable]:
        """The ``when`` condition."""
        return ()
