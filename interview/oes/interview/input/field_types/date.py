"""Date field."""

import functools
from collections.abc import Callable, Iterator, Mapping
from datetime import date
from typing import Any, Literal

from attrs import frozen
from cattrs import Converter
from oes.interview.input.field_template import FieldTemplateBase
from oes.utils.template import Expression, TemplateContext


@frozen
class DateFieldTemplate(FieldTemplateBase):
    """Date field."""

    @property
    def python_type(self) -> type[date]:
        return date

    type: Literal["date"] = "date"
    optional: bool = False

    @property
    def is_optional(self) -> bool:
        return self.optional

    default: date | None = None
    default_expr: Expression | None = None
    min: date | None = None
    max: date | None = None
    min_expr: Expression | None = None
    max_expr: Expression | None = None

    input_mode: str | None = None
    autocomplete: str | None = None

    def get_schema(self, context: TemplateContext) -> dict[str, Any]:  # noqa: CCR001
        schema = {
            **super().get_schema(context),
            "type": ["string", "null"] if self.is_optional else "string",
            "format": "date",
        }

        if self.default_expr is not None or self.default is not None:
            default_date = (
                self.default_expr.evaluate(context)
                if self.default_expr is not None
                else self.default
            )
            schema["default"] = (
                default_date.isoformat() if default_date is not None else None
            )

        if self.min_expr is not None or self.min is not None:
            min_val = (
                self.min_expr.evaluate(context)
                if self.min_expr is not None
                else self.min
            )
            schema["x-minimum"] = min_val.isoformat() if min_val is not None else None

        if self.max_expr is not None or self.max is not None:
            max_val = (
                self.max_expr.evaluate(context)
                if self.max_expr is not None
                else self.max
            )
            schema["x-maximum"] = max_val.isoformat() if max_val is not None else None

        if self.input_mode:
            schema["x-input-mode"] = self.input_mode

        if self.autocomplete:
            schema["x-autocomplete"] = self.autocomplete

        return schema

    def get_validators(
        self, context: TemplateContext
    ) -> Iterator[Callable[[Any], Any]]:
        yield self._validate_date
        if any(
            v is not None for v in (self.min, self.min_expr, self.max, self.max_expr)
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
        yield self.validate_type

    def _validate_date(self, value: Any) -> date | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Invalid date")
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError("Invalid date")

    def _validate_range(
        self, min: date | None, max: date | None, value: date | None
    ) -> date | None:
        if value is None:
            return None
        if min is not None and value < min:
            raise ValueError(f"Must be on or after {min.isoformat()}")
        if max is not None and value > max:
            raise ValueError(f"Must be on or before {max.isoformat()}")
        return value


def make_date_field_template(v: Mapping[str, Any], c: Converter) -> DateFieldTemplate:
    """Structure a date field template."""
    return c.structure(v, DateFieldTemplate)
