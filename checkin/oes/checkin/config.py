"""Config module."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

import typed_settings as ts
from attrs import Factory, field, frozen
from cattrs.preconf.orjson import make_converter
from jinja2.sandbox import ImmutableSandboxedEnvironment
from oes.utils.config import get_loaders
from oes.utils.logic import (
    ValueOrEvaluable,
    WhenCondition,
    evaluate,
    make_value_or_evaluable_structure_fn,
    make_when_condition_structure_fn,
)
from oes.utils.template import Expression, make_expression_structure_fn
from sqlalchemy import URL, make_url

if TYPE_CHECKING:
    from oes.checkin.registration import Registration


@frozen
class InterviewOption:
    """Interview option."""

    id: str
    title: str = field(default=Factory(lambda s: s.id, takes_self=True))
    when: WhenCondition = True


@frozen
class EventConfig:
    """Event config object."""

    id: str
    actions: Sequence[InterviewOption] = field(
        default=(), converter=tuple[InterviewOption, ...]
    )

    def get_allowed_actions(
        self, registration: Registration
    ) -> Iterable[InterviewOption]:
        """Get the allowed actions."""
        # TODO: user role
        ctx = {
            "registration": dict(registration),
        }
        for opt in self.actions:
            if evaluate(opt.when, ctx):
                yield opt


class _EventConfigs(dict[str, EventConfig]):
    pass


def _convert_event_configs(v: object) -> _EventConfigs:
    if isinstance(v, _EventConfigs):
        return v
    elif isinstance(v, Mapping):
        items = {ek: {**ev, "id": ek} for ek, ev in v.items()}
        return _EventConfigs(_converter.structure(items, dict[str, EventConfig]))
    else:
        raise TypeError(f"Invalid event config: {v}")


@ts.settings
class Config:
    """Config object."""

    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///checkin"),
        converter=lambda v: make_url(v),
        help="the database URL",
    )
    registration_service_url: str = ts.option(
        default="http://registration:8000", help="the registration service URL"
    )
    interview_service_url: str = ts.option(
        default="http://interview:8000", help="the interview service URL"
    )

    events: _EventConfigs = ts.option(
        default=_EventConfigs(),
        converter=_convert_event_configs,
        help="the event configuration",
    )


_converter = make_converter()


def get_config() -> Config:
    """Load the config."""
    loaders = get_loaders("OES_CHECKIN_SERVICE_", ("checkin.yml",))
    return ts.load_settings(Config, loaders, converter=cast(Any, _converter))


default_env = ImmutableSandboxedEnvironment()

_converter.register_structure_hook(URL, lambda v, t: make_url(v))
_converter.register_structure_hook(
    Expression, make_expression_structure_fn(default_env)
)
_converter.register_structure_hook(
    WhenCondition, make_when_condition_structure_fn(_converter)
)
_converter.register_structure_hook(
    ValueOrEvaluable, make_value_or_evaluable_structure_fn(_converter)
)
