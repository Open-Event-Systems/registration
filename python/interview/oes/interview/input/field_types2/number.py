"""Text field."""

from collections.abc import Callable, Iterator
from typing import Any, Optional, Type

from attrs import frozen
from oes.interview.input.field import FieldImplBase


@frozen(kw_only=True)
class NumberField(FieldImplBase[float]):
    """Number field."""

    @property
    def type(self) -> Type[float]:
        return float

    default: float | None = None

    min: Optional[float] = None
    max: Optional[float] = None
    integer: bool = False

    input_mode: str | None = None
    autocomplete: str | None = None

    @property
    def schema(self) -> dict[str, Any]:
        schema = {
            **super().schema,
            "x-type": "number",
            "type": (
                (["integer", "null"] if self.optional else "integer")
                if self.integer
                else (["number", "null"] if self.optional else "number")
            ),
        }

        if self.min is not None:
            schema["minimum"] = self.min

        if self.max is not None:
            schema["maximum"] = self.max

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        return schema

    def _validate_type(self, value: Any) -> float | None:
        if value is None or isinstance(value, (int, float)):
            return value
        else:
            raise ValueError("Invalid value")

    @property
    def validators(self) -> Iterator[Callable[[Any], float | None]]:
        yield self._validate_type
        yield self._validate_value
        yield self._validate_int
        yield self._validate_optional

    def _validate_value(self, value: float | None) -> float | None:
        if value is None:
            return None
        if self.min and value < self.min:
            raise ValueError(f"Must be at least {self.min}")
        if self.max and value > self.max:
            raise ValueError(f"Must be at most {self.max}")
        return value

    def _validate_int(self, value: float | None) -> float | int | None:
        return value if value is None else int(value) if self.integer else value
