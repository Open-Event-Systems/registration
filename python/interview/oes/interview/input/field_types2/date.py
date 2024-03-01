"""Date field."""

from collections.abc import Callable, Iterator
from datetime import date
from typing import Any, Type

from attrs import frozen
from oes.interview.input.field import FieldImplBase


@frozen(kw_only=True)
class DateField(FieldImplBase[date]):
    """Text field."""

    @property
    def type(self) -> Type[date]:
        return date

    default: date | None = None

    min: date | None = None
    max: date | None = None
    input_mode: str | None = None
    autocomplete: str | None = None

    @property
    def schema(self) -> dict[str, Any]:
        schema = {
            **super().schema,
            "x-type": "date",
            "type": ["string", "null"] if self.optional else "string",
            "format": "date",
        }

        if self.default is not None:
            schema["default"] = self.default.isoformat()

        if self.min is not None:
            schema["x-minimum"] = self.min.isoformat()

        if self.max is not None:
            schema["x-maximum"] = self.max.isoformat()

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        return schema

    @property
    def validators(self) -> Iterator[Callable[[Any], date | None]]:
        yield self._validate_date
        yield self._validate_value
        yield self._validate_optional

    def _validate_date(self, value: Any) -> date | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Invalid date")
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid date")

    def _validate_value(self, value: date | None) -> date | None:
        if value is None:
            return None
        if self.min is not None and value < self.min:
            raise ValueError(f"Must be on or after {self.min.isoformat()}")
        if self.max is not None and value > self.max:
            raise ValueError(f"Must be on or before {self.max.isoformat()}")
        return value
