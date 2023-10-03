"""Select field module."""
from collections.abc import Callable, Sequence
from typing import Any, Literal, Optional

import attr
from attrs import converters, frozen, validators
from oes.interview.input.field import OptionsFieldBase
from oes.interview.input.types import JSONSchema, Option
from oes.template import Context, Template


@frozen(kw_only=True)
class SelectFieldOption(Option):
    """A select field option."""

    id: Optional[str] = None
    """The option ID."""

    label: Template
    """The option text."""

    default: bool = False
    """Whether this option is selected by default."""

    value: Any = None
    """The option value."""

    def get_schema(
        self, context: Context, /, *, id: Optional[str] = None
    ) -> JSONSchema:
        """Get the schema for this option."""
        schema = {
            **super().get_schema(context, id=id),
            "title": self.label.render(context),
        }

        return schema


@frozen(kw_only=True)
class SelectField(OptionsFieldBase[SelectFieldOption]):
    """A select field."""

    type: Literal["select"] = "select"
    component: str = "dropdown"
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

        defaults = [id for id, opt in self.options_by_id.items() if opt.default]

        if defaults:
            schema["default"] = defaults[0] if self.is_single_value else defaults

        return schema

    @property
    def field_info(self) -> Any:
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
            converter=converters.pipe(self._convert_none, self.convert_option)
            if self.is_single_value
            else converters.pipe(self._convert_none, self.convert_options),
            validator=validators_,
        )

    def _convert_none(self, v):
        if v is None and (not self.is_single_value or not self.optional):
            raise ValueError(f"Invalid option: {v}")

        return v
