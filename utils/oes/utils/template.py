"""Template logic module."""

from collections.abc import Callable, Mapping
from datetime import date, datetime
from typing import Any, TypeAlias

import jinja2
from jinja2 import Environment
from jinja2.environment import TemplateExpression

__all__ = [
    "TemplateContext",
    "Expression",
    "Template",
    "template_fn_get_now",
    "template_filter_datetime",
    "template_filter_date",
    "make_expression_structure_fn",
    "unstructure_expression",
    "make_template_structure_fn",
    "unstructure_template",
]

TemplateContext: TypeAlias = Mapping[str, Any]
"""Template evaluation context."""


class Expression:
    """A template expression."""

    __slots__ = ("source", "_expr")

    source: str
    _expr: TemplateExpression

    def __init__(self, source: str, env: Environment):
        self.source = source
        self._expr = env.compile_expression(source, undefined_to_none=False)

    def evaluate(self, context: TemplateContext) -> Any:
        """Evaluate the expression."""
        return self._expr(**context)

    def __repr__(self) -> str:
        return f"Expression({self.source!r})"

    def __hash__(self) -> int:
        return hash(self.source)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Expression) and other.source == self.source


class Template:
    """A template."""

    __slots__ = ("source", "_template")

    source: str
    _template: jinja2.Template

    def __init__(self, source: str, env: Environment):
        self.source = source
        self._template = env.from_string(source)

    def render(self, context: TemplateContext) -> str:
        """Render the template."""
        return self._template.render(**context)

    def __repr__(self) -> str:
        return f"Template({self.source!r})"

    def __hash__(self) -> int:
        return hash(self.source)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Template) and other.source == self.source


def template_fn_get_now() -> datetime:
    """Template function to get the current datetime."""
    return datetime.now().astimezone()


def template_filter_datetime(dt: object) -> datetime | None:
    """Template filter to parse a datetime."""
    if dt is None or isinstance(dt, datetime):
        return dt
    elif isinstance(dt, (int, float)):
        return datetime.fromtimestamp(dt).astimezone()
    elif isinstance(dt, str):
        return datetime.fromisoformat(dt).astimezone()
    else:
        raise TypeError(f"Invalid datetime: {dt}")


def template_filter_date(dt: object) -> date | None:
    """Template filter to parse a date."""
    if dt is None or isinstance(dt, date):
        return dt
    elif isinstance(dt, datetime):
        return dt.date()
    elif isinstance(dt, str):
        return date.fromisoformat(dt)
    else:
        raise TypeError(f"Invalid date: {dt}")


def make_expression_structure_fn(env: Environment) -> Callable[[Any, Any], Expression]:
    """Make a function to structure an :class:`Expression`."""

    def structure(v: Any, t: Any) -> Expression:
        if not isinstance(v, str):
            raise ValueError(f"Invalid expression: {v}")
        return Expression(v, env)

    return structure


def unstructure_expression(expression: Expression) -> str:
    """Unstructure an :class:`Expression`."""
    return expression.source


def make_template_structure_fn(env: Environment) -> Callable[[Any, Any], Template]:
    """Make a function to structure a :class:`Template`."""

    def structure(v: Any, t: Any) -> Template:
        if not isinstance(v, str):
            raise ValueError(f"Invalid expression: {v}")
        return Template(v, env)

    return structure


def unstructure_template(template: Template) -> str:
    """Unstructure an :class:`Template`."""
    return template.source
