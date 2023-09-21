"""Template expression module."""
from __future__ import annotations

from typing import Any, Union

import jinja2.environment

from oes.template.env import get_jinja2_env
from oes.template.types import Context, Evaluable


class Expression(Evaluable):
    """A template expression."""

    source: str
    """The expression source."""

    _compiled: jinja2.environment.TemplateExpression

    __slots__ = (
        "source",
        "_compiled",
    )

    def __init__(self, source: Union[str, Expression]):
        """Construct a new :class:`Expression`."""
        if isinstance(source, Expression):
            self.source = source.source
            self._compiled = source._compiled
        else:
            self.source = source
            self._compiled = _compile(source)

    def evaluate(self, context: Context) -> Any:
        """Evaluate this expression."""
        return self._compiled(context)

    def __getstate__(self):
        return {"source": self.source}

    def __setstate__(self, state):
        self.source = state["source"]
        self._compiled = _compile(state["source"])

    def __repr__(self):
        return repr(self.source)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Expression) and other.source == self.source

    def __hash__(self) -> int:
        return hash(self.source)


def _compile(src: str) -> jinja2.environment.TemplateExpression:
    env = get_jinja2_env()
    return env.compile_expression(src, undefined_to_none=False)


def structure_expression(v: object, t: object) -> Expression:
    if isinstance(v, (str, Expression)):
        return Expression(v)
    else:
        raise TypeError(f"Invalid template expression: {v!r}")


def unstructure_expression(v: Expression) -> str:
    return v.source
