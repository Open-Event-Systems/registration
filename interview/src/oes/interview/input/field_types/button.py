"""Button field module."""
from collections.abc import Sequence
from typing import Any, Literal, Mapping, Optional

import attr
from attrs import frozen, validators
from oes.interview.input.field import BaseOptionsField
from oes.interview.input.types import FieldWithType, Option
from oes.interview.variables.locator import Locator
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
        self, context: Context, *, id: Optional[str] = None
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
class Button(BaseOptionsField[ButtonOption], FieldWithType):
    """A button."""

    type: Literal["button"] = "button"
    set: Optional[Locator] = None

    options: Sequence[ButtonOption] = ()

    def get_schema(self, context: Context) -> Mapping[str, object]:
        schema = {
            "x-type": "button",
            "oneOf": [
                b.get_schema(context, id=id) for id, b in self.options_by_id.items()
            ],
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
            converter=self.convert_option,
            validator=validators.not_(validators.instance_of(type(None))),
        )
