"""Config module."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import typed_settings as ts
from jinja2 import Environment
from oes.utils.config import get_loaders
from oes.utils.logic import (
    ValueOrEvaluable,
    WhenCondition,
    make_value_or_evaluable_structure_fn,
    make_when_condition_structure_fn,
)
from oes.utils.template import Expression, make_expression_structure_fn
from typed_settings.converters import get_default_cattrs_converter


@ts.settings
class ModifierConfig:
    """A modifier."""

    amount: int = ts.option(help="the modifier amount")
    name: str | None = ts.option(help="the modifier name", default=None)
    id: str | None = ts.option(help="a modifier identifier", default=None)
    when: WhenCondition = ts.option(help="the condition to include", default=())


@ts.settings
class LineItemConfig:
    """Line item."""

    price: int = ts.option(help="the item price")
    name: str | None = ts.option(help="the item name", default=None)
    description: str | None = ts.option(help="the item description", default=None)
    id: str | None = ts.option(help="a line item identifier", default=None)
    when: WhenCondition = ts.option(help="the condition to include", default=())

    modifiers: Sequence[ModifierConfig] = ts.option(help="modifiers", default=())


@ts.settings
class EventConfig:
    """Per-event config."""

    script_dir: Path | None = ts.option(help="pricing script directory", default=None)
    items: Sequence[LineItemConfig] = ts.option(help="item config", default=())

    modifiers: Sequence[ModifierConfig] = ts.option(help="modifiers", default=())


@ts.settings
class Config:
    """Config settings."""

    events: Mapping[str, EventConfig] = ts.option(help="per-event config", factory=dict)


def get_config() -> Config:
    """Get config settings."""
    jinja2_env = Environment()
    converter = get_default_cattrs_converter()
    converter.register_structure_hook(
        Expression, make_expression_structure_fn(jinja2_env)
    )
    converter.register_structure_hook(
        ValueOrEvaluable, make_value_or_evaluable_structure_fn(converter)
    )
    converter.register_structure_hook(
        WhenCondition, make_when_condition_structure_fn(converter)
    )
    return ts.load_settings(
        Config,
        get_loaders("OES_PRICING_", ("pricing.yml",)),
        converter=cast(Any, converter),
    )
