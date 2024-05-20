"""Configuration module."""

from collections.abc import Sequence
from datetime import date
from typing import Any, TypeAlias, cast

import typed_settings as ts
from jinja2.sandbox import ImmutableSandboxedEnvironment
from oes.utils.config import get_loaders
from oes.utils.logic import (
    LogicAnd,
    LogicOr,
    WhenCondition,
    make_logic_unstructure_fn,
    make_when_condition_structure_fn,
)
from oes.utils.template import (
    Expression,
    Template,
    TemplateContext,
    make_template_structure_fn,
)

dt_date: TypeAlias = date

jinja2_env = ImmutableSandboxedEnvironment()


@ts.settings
class InterviewOption:
    """Interview option."""

    id: str
    title: str | None = None
    when: WhenCondition = True


@ts.settings
class RegistrationDisplay:
    """Registration display options."""

    title: Template = Template("Registration", jinja2_env)
    subtitle: Template | None = None
    description: Template | None = None
    header_color: Template | None = None
    header_image: Template | None = None


@ts.settings
class Event:
    """Event config."""

    id: str
    date: dt_date
    title: str | None = None
    description: str | None = None
    open: bool = False
    visible: bool = False

    add_options: Sequence[InterviewOption] = ()
    change_options: Sequence[InterviewOption] = ()

    registration_display: RegistrationDisplay = RegistrationDisplay()

    def get_template_context(self) -> TemplateContext:
        """Get the template context for evaluating conditions."""
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "description": self.description,
            "open": self.open,
            "visible": self.visible,
        }


@ts.settings
class Config:
    """Main config object."""

    events: Sequence[Event] = ()


_converter = ts.converters.get_default_cattrs_converter()
_converter.register_structure_hook(Template, make_template_structure_fn(jinja2_env))
_converter.register_structure_hook(Expression, make_template_structure_fn(jinja2_env))
_converter.register_structure_hook(
    WhenCondition, make_when_condition_structure_fn(_converter)
)
_converter.register_unstructure_hook(LogicAnd, make_logic_unstructure_fn(_converter))
_converter.register_unstructure_hook(LogicOr, make_logic_unstructure_fn(_converter))


def get_config() -> Config:
    """Get the config."""
    return ts.load_settings(
        Config,
        get_loaders("OES_WEB_", ("events.yml",)),
        converter=cast(Any, _converter),
    )
