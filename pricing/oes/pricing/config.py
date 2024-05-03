"""Config module."""

from collections.abc import Mapping
from pathlib import Path

import typed_settings as ts
from oes.utils.config import get_loaders


@ts.settings
class Modifier:
    """An option modifier."""


@ts.settings
class Option:
    """Registration option."""

    name: str | None = ts.option(help="the option name", default=None)
    price: int = ts.option(help="the option price")


@ts.settings
class EventConfig:
    """Per-event config."""

    script_dir: Path = ts.option(help="pricing script directory")


@ts.settings
class Config:
    """Config settings."""

    events: Mapping[str, EventConfig] = ts.option(help="per-event config", factory=dict)


def get_config() -> Config:
    """Get config settings."""
    return ts.load_settings(Config, get_loaders("OES_PRICING_", ("pricing.yml",)))
