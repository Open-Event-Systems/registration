"""Number field type."""
from typing import Any, Literal, Mapping, Optional

import attr
from attrs import frozen, validators
from oes.interview.input.field import BaseField
from oes.interview.input.types import Context


@frozen(kw_only=True)
class NumberField(BaseField):
    """A number field."""

    type: Literal["number"] = "number"
    default: Optional[float] = None

    integer: bool = False
    """Restrict to integers."""

    min: Optional[float] = None
    """The minimum value."""

    max: Optional[float] = None
    """The maximum value."""

    input_mode: Optional[str] = None
    """The HTML input mode for this field."""

    autocomplete: Optional[str] = None
    """The autocomplete type for this field's input."""

    @property
    def value_type(self) -> object:
        return int if self.integer else float

    @property
    def field_info(self) -> Any:
        validators_ = []

        if self.min is not None:
            validators_.append(validators.ge(self.min))

        if self.max is not None:
            validators_.append(validators.le(self.max))

        return attr.ib(
            type=self.optional_type,
            validator=[
                *self.validators,
                validators.optional(validators_),
            ],
        )

    def get_schema(self, context: Context) -> Mapping[str, object]:
        schema = {
            "type": "integer" if self.integer else "number",
            "x-type": "number",
            "nullable": self.optional,
        }

        if self.min is not None:
            schema["minimum"] = self.min

        if self.max is not None:
            schema["maximum"] = self.max

        if self.label:
            schema["title"] = self.label.render(context)

        if self.default:
            schema["default"] = self.default

        return schema
