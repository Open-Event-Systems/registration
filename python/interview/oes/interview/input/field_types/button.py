"""Button field module."""
from collections.abc import Sequence
from typing import Any, Literal, Mapping, Optional

import attr
from attrs import converters, frozen
from oes.interview.input.field import OptionsFieldBase
from oes.interview.input.types import FieldType, Option
from oes.template import Context, Template


@frozen(kw_only=True)
class ButtonOption(Option):
    """A button option."""

    id: Optional[str] = None
    """The button ID."""

    label: Template
    """The button text."""

    primary: bool = False
    """Whether the button has the "primary" style."""

    default: bool = False
    """Whether the button is the default option."""

    value: Any = None
    """The button value."""

    def get_schema(
        self, context: Context, /, *, id: Optional[str] = None
    ) -> Mapping[str, object]:
        """Get the schema for this button."""
        schema = {
            **super().get_schema(context, id=id),
            "title": self.label.render(context),
        }

        if self.primary:
            schema["x-primary"] = self.primary

        return schema


@frozen(kw_only=True)
class Button(OptionsFieldBase[ButtonOption]):
    """A button."""

    type: Literal[FieldType.button] = FieldType.button
    options: Sequence[ButtonOption] = ()

    def get_schema(self, context: Context) -> Mapping[str, object]:
        options = [b.get_schema(context, id=id) for id, b in self.options_by_id.items()]

        schema = {
            **super().get_schema(context),
            "oneOf": options,
        }

        default = next(
            (id_ for id_, b in self.options_by_id.items() if b.default), None
        )

        if default is not None:
            schema["default"] = default

        return schema

    @property
    def field_info(self) -> Any:
        return attr.ib(
            type=Any,
            converter=converters.pipe(self._convert_none, self.convert_option),
        )

    def _convert_none(self, v):
        if v is None:
            raise ValueError("Value is required")
        return v
