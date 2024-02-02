"""Button field module."""

from collections.abc import Sequence
from typing import Any, Literal, Mapping

import attr
from attrs import converters, frozen
from oes.interview.input.field import OptionsFieldBase
from oes.interview.input.types import FieldType
from oes.template import Context, Expression, Template


@frozen(kw_only=True)
class ButtonOption:
    """A button option."""

    id: str | None = None
    """The button ID."""

    label: Template
    """The button text."""

    primary: bool = False
    """Whether the button has the "primary" style."""

    primary_expr: Expression | None = None
    """An expression of whether the button has the "primary" style."""

    default: bool = False
    """Whether the button is the default option."""

    default_expr: Expression | None = None
    """An expression of whether the button is the default option."""

    value: Any = None
    """The button value."""

    value_expr: Expression | None = None
    """An expression of the button value."""

    def get_schema(
        self, context: Context, *, id: str | None = None
    ) -> Mapping[str, object]:
        """Get the schema for this button."""
        if id is None and self.id is None:
            raise ValueError("An ID must be provided")

        schema = {
            "const": id or self.id,
            "title": self.label.render(context),
        }

        primary_val = (
            self.primary_expr.evaluate(context)
            if self.primary_expr is not None
            else self.primary
        )

        if primary_val:
            schema["x-primary"] = True

        return schema


@frozen(kw_only=True)
class Button(OptionsFieldBase[ButtonOption]):
    """A button."""

    type: Literal[FieldType.button] = FieldType.button
    options: Sequence[ButtonOption] = ()

    @property
    def optional(self) -> Literal[False]:
        return False

    def get_schema(self, context: Context) -> Mapping[str, object]:
        options = [b.get_schema(context, id=id) for id, b in self.options_by_id.items()]

        schema = {
            **super().get_schema(context),
            "oneOf": options,
        }

        default = next(
            (
                id_
                for id_, b in self.options_by_id.items()
                if b.default_expr and b.default_expr.evaluate(context) or b.default
            ),
            None,
        )

        if default is not None:
            schema["default"] = default

        return schema

    def get_field_info(self, context: Context) -> Any:
        return attr.ib(
            type=Any,
            converter=converters.pipe(
                self._convert_none, lambda x: self.convert_option(x, context)
            ),
        )

    def _convert_none(self, v):
        if v is None:
            raise ValueError("Value is required")
        return v
