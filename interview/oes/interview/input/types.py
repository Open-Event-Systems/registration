"""Input types."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias

from oes.utils.template import TemplateContext

if TYPE_CHECKING:
    from oes.interview.input.field import Field
    from oes.interview.logic.types import ValuePointer


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

    @property
    @abstractmethod
    def set(self) -> ValuePointer | None:
        """The value this field sets."""
        ...

    @abstractmethod
    def get_field(self, context: TemplateContext) -> Field:
        """Get a :class:`Field` from this template."""
        ...


# _T_co = TypeVar("_T_co", covariant=True)


# class Field(Protocol[_T_co]):
#     """An input field."""

#     @property
#     @abstractmethod
#     def python_type(self) -> Type[_T_co]:
#         """The Python type of the field's value."""
#         ...

#     @property
#     @abstractmethod
#     def optional(self) -> bool:
#         """Whether the field value can be ``None``."""
#         ...

#     @property
#     @abstractmethod
#     def schema(self) -> JSONSchema:
#         """The JSON schema describing the field."""
#         ...

#     @abstractmethod
#     def parse(self, value: object) -> _T_co | None:
#         """Parse/validate the input value.

#         Raises:
#             ValueError: If the response is invalid.
#         """
#         ...


# class RequiredField(Field[_T_co], Protocol[_T_co]):
#     """A required field."""

#     @property
#     @abstractmethod
#     def optional(self) -> Literal[False]:
#         ...

#     @abstractmethod
#     def parse(self, value: object) -> _T_co:
#         ...


# class OptionalField(Field[_T_co], Protocol[_T_co]):
#     """An optional field."""

#     @property
#     @abstractmethod
#     def optional(self) -> Literal[True]:
#         ...

#     @abstractmethod
#     def parse(self, value: object) -> _T_co | None:
#         ...


# class FieldTemplate(Protocol[_T_co]):
#     """A field template."""

#     @property
#     @abstractmethod
#     def python_type(self) -> Type[_T_co]:
#         """The Python type of the field's value."""
#         ...

#     @property
#     @abstractmethod
#     def type(self) -> str:
#         """The field type."""
#         ...

#     @property
#     @abstractmethod
#     def set(self) -> ValuePointer | None:
#         """The value this field sets."""
#         ...

#     @property
#     @abstractmethod
#     def label(self) -> str | Template | None:
#         """A label for the field."""
#         ...

#     @property
#     @abstractmethod
#     def optional(self) -> bool:
#         """Whether the field may be ``None``."""
#         ...

#     @abstractmethod
#     def get_field(self, context: Context) -> Field[_T_co]:
#         """Get a :class:`Field` from this template."""
#         ...


# FieldTemplateFactory: TypeAlias = Callable[
#     [Mapping[str, Any], Converter], FieldTemplate[Any]
# ]


# class Question(Protocol):
#     """A question."""

#     @property
#     @abstractmethod
#     def schema(self) -> JSONSchema:
#         """The question JSON schema."""
#         ...

#     @abstractmethod
#     def parse(self, response: Mapping[str, Any]) -> Mapping[ValuePointer, Any]:
#         """Parse the user response.

#         Raises:
#             ValueError: If the response is invalid.
#         """
#         ...


# class QuestionTemplate(Protocol):
#     """A :class:`Question` template."""

#     @property
#     @abstractmethod
#     def id(self) -> str | None:
#         """An ID for the question."""
#         ...

#     @property
#     @abstractmethod
#     def provides(self) -> Collection[ValuePointer]:
#         """The values provided by this question."""
#         ...

#     @abstractmethod
#     def get_question(self, context: Context) -> Question:
#         """Get a :class:`Question` object."""
#         ...
