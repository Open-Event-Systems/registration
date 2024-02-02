"""Select field module."""

from collections.abc import Callable, Sequence
from enum import Enum
from typing import Any, Literal

import attr
from attrs import converters, frozen, validators
from oes.interview.input.field import OptionsFieldBase
from oes.interview.input.types import FieldType, JSONSchema
from oes.template import Context, Expression, Template


class SelectComponentType(str, Enum):
    """Component type IDs for select fields."""

    dropdown = "dropdown"
    checkbox = "checkbox"
    radio = "radio"


@frozen(kw_only=True)
class SelectFieldOption:
    """A select field option."""

    id: str | None = None
    """The option ID."""

    label: Template
    """The option text."""

    default: bool = False
    """Whether this option is selected by default."""

    default_expr: Expression | None = None
    """An expression of whether this option is selected by default."""

    value: Any = None
    """The option value."""

    value_expr: Expression | None = None
    """An expression of the value."""

    def get_schema(self, context: Context, *, id: str | None = None) -> JSONSchema:
        """Get the schema for this option."""
        if id is None and self.id is None:
            raise ValueError("An ID must be provided")

        schema = {
            "const": id or self.id,
            "title": self.label.render(context),
        }

        return schema


@frozen(kw_only=True)
class SelectField(OptionsFieldBase[SelectFieldOption]):
    """A select field."""

    type: Literal[FieldType.select] = FieldType.select
    component: SelectComponentType = SelectComponentType.dropdown
    """The component type to display."""

    min: int = 1
    max: int = 1

    options: Sequence[SelectFieldOption] = ()

    @property
    def is_single_value(self) -> bool:
        return self.max == 1

    @property
    def optional(self) -> bool:
        return self.min == 0

    def get_schema(self, context: Context) -> JSONSchema:
        options = [b.get_schema(context, id=id) for id, b in self.options_by_id.items()]
        if self.is_single_value:
            if self.optional:
                options.append({"type": "null"})

            schema = {
                **super().get_schema(context),
                "x-component": self.component,
                "oneOf": options,
            }
        else:
            schema = {
                **super().get_schema(context),
                "type": "array",
                "x-component": self.component,
                "items": {
                    "oneOf": options,
                },
                "minItems": self.min,
                "maxItems": self.max,
                "uniqueItems": True,
            }

        defaults = [
            id
            for id, opt in self.options_by_id.items()
            if opt.default_expr and opt.default_expr.evaluate(context) or opt.default
        ]

        if defaults:
            schema["default"] = defaults[0] if self.is_single_value else defaults

        return schema

    def get_field_info(self, context: Context) -> Any:
        if not self.is_single_value:
            validators_: list[Callable[[Any, Any, Any], Any]] = [
                validators.instance_of(
                    tuple,
                ),
                validators.min_len(self.min),
                validators.max_len(self.max),
            ]
        else:
            validators_ = []

        return attr.ib(
            type=Any,
            converter=(
                converters.pipe(
                    self._convert_none, lambda x: self.convert_option(x, context)
                )
                if self.is_single_value
                else converters.pipe(
                    self._convert_none, lambda x: self.convert_options(x, context)
                )
            ),
            validator=validators_,
        )

    def _convert_none(self, v):
        if v is None and (not self.is_single_value or not self.optional):
            raise ValueError(f"Invalid option: {v}")

        return v
