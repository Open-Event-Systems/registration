"""Select field."""

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from enum import Enum
from typing import Any, Type

from attrs import Factory, field, frozen
from oes.interview.logic.types import ValuePointer


class SelectComponentType(str, Enum):
    """select component types."""

    dropdown = "dropdown"
    checkbox = "checkbox"
    radio = "radio"


@frozen
class SelectOption:
    """Text field option."""

    id: str
    label: str | None = None
    value: Any = None
    default: bool = False

    @property
    def schema(self) -> dict[str, Any]:
        """Option schema."""
        return {
            "const": self.id,
            "title": self.label,
        }


@frozen(kw_only=True)
class SelectField:
    """Select field."""

    @property
    def type(self) -> Type[Any]:
        return object

    set: ValuePointer | None = None
    component: str = SelectComponentType.dropdown
    options: Sequence[SelectOption] = ()
    label: str | None = None
    min: int = 1
    max: int = 1

    input_mode: str | None = None
    autocomplete: str | None = None

    _values_by_id: Mapping[str, Any] = field(
        default=Factory(lambda s: {o.id: o.value for o in s.options}, takes_self=True),
        init=False,
        eq=False,
    )

    @property
    def optional(self) -> bool:
        return self.min == 0

    @property
    def multi(self) -> bool:
        return self.max > 1

    @property
    def schema(self) -> dict[str, Any]:
        schema = {"x-type": "select", "x-component": self.component}

        if self.label:
            schema["title"] = self.label

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        return (
            self._get_multi_schema(schema)
            if self.multi
            else self._get_scalar_schema(schema)
        )

    def _get_scalar_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        option_schemas = [o.schema for o in self.options]
        schema = {
            **schema,
            "type": ["string", "null"] if self.optional else "string",
            "oneOf": option_schemas + [{"type": "null"}] if self.optional else [],
        }

        if self.min > 0:
            schema["minItems"] = self.min

        default_id = next((o.id for o in self.options if o.default), None)

        if default_id:
            schema["default"] = default_id

        return schema

    def _get_multi_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        option_schemas = [o.schema for o in self.options]
        schema = {
            **schema,
            "type": "array",
            "items": {
                "oneOf": option_schemas,
            },
            "maxItems": self.max,
        }

        if self.min > 0:
            schema["minItems"] = self.min

        default_ids = [o.id for o in self.options if o.default]

        if default_ids:
            schema["default"] = default_ids if self.multi else default_ids[0]

        return schema

    def __call__(self, value: object, /) -> Any:
        for validator in self._validators():
            value = validator(value)
        return value

    def _validators(self) -> Iterator[Callable[[Any], Any]]:
        yield self._validate_duplicates
        yield self._validate_values
        if self.multi:
            yield self._validate_count

    def _validate_duplicates(self, value: Any) -> Any:
        if (
            isinstance(value, Sequence)
            and not isinstance(value, str)
            and all(isinstance(v, str) for v in value)
        ):
            values = {k: None for k in value}
            return list(values)  # preserve order
        else:
            return value

    def _validate_values(self, value: Any) -> Any:
        if value is None and self.optional:
            return [] if self.multi else None
        elif self.multi and isinstance(value, Sequence) and not isinstance(value, str):
            return self._convert_values(value)
        elif not self.multi:
            return self._convert_value(value)
        else:
            raise ValueError(f"Invalid value: {value}")

    def _convert_values(self, values: Iterable[Any]) -> list[Any]:
        return [self._convert_value(v) for v in values]

    def _convert_value(self, value_id: Any) -> Any:
        if not isinstance(value_id, str) or value_id not in self._values_by_id:
            raise ValueError(f"Invalid value: {value_id}")
        return self._values_by_id[value_id]

    def _validate_count(self, value: Sequence[Any]) -> Sequence[Any]:
        if len(value) < self.min:
            raise ValueError(f"Choose at least {self.min}")
        if len(value) > self.max:
            raise ValueError(f"Choose at most {self.max}")
        return value
