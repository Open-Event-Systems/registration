"""Button field."""

from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal, Mapping

from attrs import field, frozen
from cattrs import Converter
from oes.interview.input.field_template import (
    SelectFieldOptionBase,
    SelectFieldTemplateBase,
)
from oes.utils.template import TemplateContext


@frozen
class ButtonFieldOption(SelectFieldOptionBase):
    """Button field option."""

    default: bool = False
    primary: bool = False

    def get_schema(self, id: str, context: TemplateContext) -> dict[str, Any]:
        schema = super().get_schema(id, context)
        if self.primary:
            schema["x-primary"] = True
        return schema


@frozen
class ButtonFieldTemplate(SelectFieldTemplateBase):
    """Button field."""

    @property
    def python_type(self) -> type:
        return object

    type: Literal["button"] = "button"
    options: Sequence[ButtonFieldOption] = field(
        default=(), converter=tuple[ButtonFieldOption, ...]
    )

    @property
    def multi(self) -> bool:
        return False

    @property
    def is_optional(self) -> bool:
        return False

    def get_schema(self, context: Mapping[str, Any]) -> dict[str, Any]:
        schema = super().get_schema(context)
        options = self.get_options(context)
        defaults = [opt_id for opt_id, opt in options.items() if opt.default]
        if defaults:
            schema["default"] = next(iter(defaults), None)

        return schema

    def get_validators(
        self, context: TemplateContext
    ) -> Iterable[Callable[[Any], Any]]:
        yield from super().get_validators(context)


def make_button_field_template(
    v: Mapping[str, Any], c: Converter
) -> ButtonFieldTemplate:
    """Structure a button field template."""
    return c.structure(v, ButtonFieldTemplate)
