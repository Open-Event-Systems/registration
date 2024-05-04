"""Number field type."""

import functools
from collections.abc import Callable, Iterator, Mapping
from typing import Any, Literal, TypeAlias, Union

from attrs import field, frozen
from cattrs import Converter
from oes.interview.input.field_template import FieldTemplateBase
from oes.utils.template import Expression, TemplateContext

_Num: TypeAlias = Union[int, float]


@frozen
class NumberFieldTemplate(FieldTemplateBase):
    """Number field template."""

    @property
    def python_type(self) -> type[int] | type[float]:
        return int if self.integer else float

    type: Literal["number"] = "number"
    _optional: bool = field(default=False, alias="optional")
    default: _Num | None = None
    default_expr: Expression | None = None
    min: _Num | None = None
    max: _Num | None = None
    min_expr: Expression | None = None
    max_expr: Expression | None = None
    integer: bool = False

    input_mode: str | None = None
    autocomplete: str | None = None

    @property
    def optional(self) -> bool:
        return self._optional

    def get_schema(self, context: TemplateContext) -> dict[str, Any]:
        typ = "integer" if self.integer else "number"
        schema = {
            **super().get_schema(context),
            "type": [typ, "null"] if self.optional else typ,
        }

        if self.default_expr is not None or self.default is not None:
            schema["default"] = (
                self.default_expr.evaluate(context)
                if self.default_expr is not None
                else self.default
            )

        if self.min is not None:
            schema["minimum"] = self.min

        if self.max is not None:
            schema["maximum"] = self.max

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        return schema

    def get_validators(
        self, context: TemplateContext
    ) -> Iterator[Callable[[Any], Any]]:
        yield self.validate_type

        if any(
            v is not None for v in (self.min, self.max, self.min_expr, self.max_expr)
        ):
            min_val = (
                self.min_expr.evaluate(context)
                if self.min_expr is not None
                else self.min
            )
            max_val = (
                self.max_expr.evaluate(context)
                if self.max_expr is not None
                else self.max
            )
            yield functools.partial(self._validate_range, min_val, max_val)

        yield self._validate_int
        yield self.validate_type

    def _validate_range(self, min, max, value):
        if value is None:
            return None
        if min and value < min:
            raise ValueError(f"Must be at least {min}")
        if max and value > max:
            raise ValueError(f"Must be at most {max}")
        return value

    def validate_type(self, value: Any) -> float | None:
        if value is None and not self.optional or not isinstance(value, (int, float)):
            raise ValueError("Invalid value")
        return value

    def _validate_int(self, value: float | None) -> float | int | None:
        return value if value is None else int(value) if self.integer else value


def make_number_field_template(
    v: Mapping[str, Any], c: Converter
) -> NumberFieldTemplate:
    """Structure a number field template."""
    return c.structure(v, NumberFieldTemplate)
