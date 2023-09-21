"""Template module."""
from __future__ import annotations

from typing import Union

import jinja2.environment

from oes.template.env import get_jinja2_env
from oes.template.types import Context


class Template:
    """A Jinja2 template."""

    source: str
    """The template source."""

    _compiled: jinja2.Template

    __slots__ = (
        "source",
        "_compiled",
    )

    def __init__(self, source: Union[str, Template]):
        """Construct a new :class:`Template`."""
        if isinstance(source, Template):
            self.source = source.source
            self._compiled = source._compiled
        else:
            self.source = source
            self._compiled = _compile(source)

    def render(self, context: Context) -> str:
        """Render the template."""
        return self._compiled.render(context)

    def __getstate__(self):
        return {"source": self.source}

    def __setstate__(self, state):
        self.source = state["source"]
        self._compiled = _compile(state["source"])

    def __repr__(self):
        return repr(self.source)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Template) and other.source == self.source

    def __hash__(self) -> int:
        return hash(self.source)


def _compile(src: str) -> jinja2.Template:
    env = get_jinja2_env()
    return env.from_string(src)


def structure_template(v: object, t: object) -> Template:
    if isinstance(v, (str, Template)):
        return Template(v)
    else:
        raise TypeError(f"Invalid template: {v!r}")


def unstructure_template(v: Template) -> str:
    return v.source
