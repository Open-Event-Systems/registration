"""Number field type."""

from typing import Any, Callable, Literal, Type

import attr
from attr import Attribute
from attrs import frozen, validators
from oes.interview.input.field import FieldBase
from oes.interview.input.types import Context, FieldType, JSONSchema


@frozen(kw_only=True)
class NumberField(FieldBase):
    """A number field."""

    type: Literal[FieldType.number] = FieldType.number
    default: float | None = None

    integer: bool = False
    """Restrict to integers."""

    min: float | None = None
    """The minimum value."""

    max: float | None = None
    """The maximum value."""

    input_mode: str | None = None
    """The HTML input mode for this field."""

    autocomplete: str | None = None
    """The autocomplete type for this field's input."""

    @property
    def value_type(self) -> Type:
        return int if self.integer else float

    @property
    def validators(self) -> list[Callable[[Any, Attribute, Any], Any]]:
        validators_ = super().validators
        extra_validators = []

        if self.min is not None:
            extra_validators.append(validators.ge(self.min))

        if self.max is not None:
            extra_validators.append(validators.le(self.max))

        return [*validators_, validators.optional(extra_validators)]

    def get_field_info(self, context: Context) -> Any:
        return attr.ib(
            type=self.optional_type,
            converter=self._converter,
            validator=self.validators,
        )

    def _converter(self, v):
        if isinstance(v, (int, float)):
            return int(v) if self.integer else float(v)
        else:
            return v

    def get_schema(self, context: Context) -> JSONSchema:
        num_type = "integer" if self.integer else "number"

        schema = {
            **super().get_schema(context),
            "type": [num_type, "null"] if self.optional else num_type,
        }

        if self.min is not None:
            schema["minimum"] = self.min

        if self.max is not None:
            schema["maximum"] = self.max

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        return schema
