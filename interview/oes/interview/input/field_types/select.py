"""Select field."""

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
class SelectFieldOption(SelectFieldOptionBase):
    """Select field option."""

    default: bool = False
    primary: bool = False

    def get_schema(self, id: str, context: TemplateContext) -> dict[str, Any]:
        schema = super().get_schema(id, context)
        if self.primary:
            schema["x-primary"] = True
        return schema


@frozen
class SelectFieldTemplate(SelectFieldTemplateBase):
    """Select field."""

    @property
    def python_type(self) -> type:
        return object

    type: Literal["select"] = "select"
    component: str = "dropdown"
    options: Sequence[SelectFieldOption] = field(
        default=(), converter=tuple[SelectFieldOption, ...]
    )
    min: int = 0
    max: int = 1

    @property
    def multi(self) -> bool:
        return self.max > 1

    @property
    def is_optional(self) -> bool:
        return self.min == 0

    autocomplete: str | None = None

    def get_schema(self, context: Mapping[str, Any]) -> dict[str, Any]:
        schema = super().get_schema(context)
        options = self.get_options(context)
        defaults = [opt_id for opt_id, opt in options.items() if opt.default]
        if self.multi:
            schema["minItems"] = self.min
            schema["maxItems"] = self.max
            if defaults:
                schema["default"] = defaults
        else:
            if defaults:
                schema["default"] = next(iter(defaults), None)

        if self.autocomplete:
            schema["x-autoComplete"] = self.autocomplete

        schema["x-component"] = self.component

        return schema

    def get_validators(
        self, context: TemplateContext
    ) -> Iterable[Callable[[Any], Any]]:
        yield from super().get_validators(context)
        if self.multi:
            yield self._validate_size

    def _validate_size(self, values: Sequence[Any]) -> Sequence[Any]:
        if len(values) < self.min:
            raise ValueError(f"Choose at least {self.min}")
        if len(values) > self.max:
            raise ValueError(f"Choose at most {self.max}")
        return values


def make_select_field_template(
    v: Mapping[str, Any], c: Converter
) -> SelectFieldTemplate:
    """Structure a select field template."""
    return c.structure(v, SelectFieldTemplate)
