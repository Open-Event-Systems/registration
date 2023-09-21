"""Date field type."""
from datetime import date
from typing import Any, Literal, Mapping, Optional

import attr
from attrs import frozen, validators
from oes.interview.input.field import BaseField
from oes.interview.input.types import Context


@frozen(kw_only=True)
class DateField(BaseField):
    """A date field."""

    type: Literal["date"] = "date"
    default: Optional[date] = None

    min: Optional[date] = None
    """The minimum value."""

    max: Optional[date] = None
    """The maximum value."""

    @property
    def value_type(self) -> object:
        return date

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
            "type": "string",
            "format": "date",
            "x-type": "date",
            "nullable": self.optional,
        }

        if self.min is not None:
            schema["x-minimum"] = self.min

        if self.max is not None:
            schema["x-maximum"] = self.max

        if self.label:
            schema["title"] = self.label.render(context)

        if self.default:
            schema["default"] = self.default

        return schema
