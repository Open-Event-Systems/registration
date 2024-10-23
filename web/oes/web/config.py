"""Configuration module."""

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any, TypeAlias, cast

import typed_settings as ts
from attrs import Factory, field, frozen
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
    make_expression_structure_fn,
    make_template_structure_fn,
)

dt_date: TypeAlias = date

jinja2_env = ImmutableSandboxedEnvironment()


@frozen
class ConfigInterviewOption:
    """Interview option."""

    id: str
    title: str
    direct: bool = False
    when: WhenCondition = True


@frozen
class RegistrationDisplay:
    """Registration display options."""

    title: Template = Template("Registration", jinja2_env)
    subtitle: Template | None = None
    description: Template | None = None
    header_color: Template | None = None
    header_image: Template | None = None


@frozen
class SelfServiceConfig:
    """Self service configuration."""

    add_options: Sequence[ConfigInterviewOption] = ()
    change_options: Sequence[ConfigInterviewOption] = ()

    display: RegistrationDisplay = RegistrationDisplay()


@frozen
class Event:
    """Event config."""

    id: str
    date: dt_date
    title: str = field(default=Factory(lambda s: s.id, takes_self=True))
    description: str | None = None
    open: bool = False
    visible: bool = False

    self_service: SelfServiceConfig = SelfServiceConfig()

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


class _EventMapping(dict[str, Event]):
    pass


@ts.settings
class Config:
    """Main config object."""

    cart_service_url: str = ts.option(
        default="http://cart:8000", help="the cart service url"
    )
    payment_service_url: str = ts.option(
        default="http://payment:8000", help="the payment service url"
    )
    registration_service_url: str = ts.option(
        default="http://registration:8000", help="the registration service url"
    )
    interview_service_url: str = ts.option(
        default="http://interview:8000", help="the interview service url"
    )
    events: _EventMapping = ts.option(help="the events", default=_EventMapping())

    def get_event(self, event_id: str) -> Event | None:
        """Get an event by ID."""
        return self.events.get(event_id)


def _structure_event_mapping(v: Any, t: Any) -> _EventMapping:
    if isinstance(v, _EventMapping):
        return v
    if not isinstance(v, Mapping):
        raise TypeError(f"Not a mapping: {v}")
    items = {k: {**v, "id": k} for k, v in v.items()}
    return _EventMapping(_converter.structure(items, Mapping[str, Event]))


_converter = ts.converters.get_default_cattrs_converter()
_converter.register_structure_hook(Template, make_template_structure_fn(jinja2_env))
_converter.register_structure_hook(Expression, make_expression_structure_fn(jinja2_env))
_converter.register_structure_hook(
    WhenCondition, make_when_condition_structure_fn(_converter)
)
_converter.register_unstructure_hook(LogicAnd, make_logic_unstructure_fn(_converter))
_converter.register_unstructure_hook(LogicOr, make_logic_unstructure_fn(_converter))
_converter.register_structure_hook(_EventMapping, _structure_event_mapping)


def get_config(config_file: str = "events.yml") -> Config:
    """Get the config."""
    return ts.load_settings(
        Config,
        get_loaders("OES_WEB_", (config_file,)),
        converter=cast(ts.converters.Converter, _converter),
    )
