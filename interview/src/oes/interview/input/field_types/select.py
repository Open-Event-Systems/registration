"""Select field module."""
from collections.abc import Sequence
from typing import Any, Literal, Mapping, Optional

import attr
from attrs import frozen, validators
from oes.interview.input.field import BaseOptionsField
from oes.interview.input.types import FieldWithType, Option
from oes.interview.variables.locator import Locator
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
        self, context: Context, *, id: Optional[str] = None
    ) -> Mapping[str, object]:
        """Get the schema for this option."""
        schema = {
            **super().get_schema(context, id=id),
            "title": self.label.render(context),
        }

        return schema


@frozen(kw_only=True)
class SelectField(BaseOptionsField[SelectFieldOption], FieldWithType):
    """A select field."""

    type: Literal["select"] = "select"
    set: Optional[Locator] = None

    label: Optional[Template] = None
    """The field label."""

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

    def get_schema(self, context: Context) -> Mapping[str, object]:
        options = [b.get_schema(context, id=id) for id, b in self.options_by_id.items()]
        if self.is_single_value:
            if self.optional:
                options.append({"type": "null"})

            schema = {
                "type": "string",
                "x-type": "select",
                "x-component": self.component,
                "oneOf": options,
                "nullable": self.optional,
            }
        else:
            schema = {
                "type": "array",
                "x-type": "select",
                "x-component": self.component,
                "items": {
                    "oneOf": options,
                },
                "minItems": self.min,
                "maxItems": self.max,
                "uniqueItems": True,
            }

        if self.label:
            schema["title"] = self.label.render(context)

        defaults = [id for id, opt in self.options_by_id.items() if opt.default]

        if defaults:
            schema["default"] = defaults[0] if self.is_single_value else defaults

        return schema

    @property
    def field_info(self) -> Any:
        validators_ = []
        if self.is_single_value:
            if not self.optional:
                validators_.append(validators.not_(validators.instance_of(type(None))))

            return attr.ib(
                type=Any,
                converter=self.convert_option,
                validator=validators_,
            )
        else:
            validators_.append(validators.instance_of(list))  # type: ignore
            validators_.append(validators.min_len(self.min))
            validators_.append(validators.max_len(self.max))

            return attr.ib(
                type=list,
                converter=self.convert_options,
                validator=validators_,
            )
