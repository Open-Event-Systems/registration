"""Date field type."""
from datetime import date
from typing import Any, Callable, Literal, Optional, Type

from attr import Attribute
from attrs import frozen, validators
from oes.interview.input.field import FieldBase
from oes.interview.input.types import Context, FieldType, JSONSchema


@frozen(kw_only=True)
class DateField(FieldBase):
    """A date field."""

    type: Literal[FieldType.date] = FieldType.date
    default: Optional[date] = None

    min: Optional[date] = None
    """The minimum value."""

    max: Optional[date] = None
    """The maximum value."""

    autocomplete: Optional[str] = None
    """The autocomplete type for this field's input."""

    @property
    def value_type(self) -> Type:
        return date

    @property
    def validators(self) -> list[Callable[[Any, Attribute, Any], Any]]:
        extra_validators = []

        if self.min is not None:
            extra_validators.append(validators.ge(self.min))

        if self.max is not None:
            extra_validators.append(validators.le(self.max))

        return [
            *super().validators,
            validators.optional(extra_validators),
        ]

    def get_schema(self, context: Context) -> JSONSchema:
        schema = {
            **super().get_schema(context),
            "type": ["string", "null"] if self.optional else "string",
            "format": "date",
        }

        if self.min is not None:
            schema["x-minimum"] = self.min

        if self.max is not None:
            schema["x-maximum"] = self.max

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        return schema
