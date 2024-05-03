"""Config module."""

from pathlib import Path

import typed_settings as ts
from oes.utils.config import get_loaders


@ts.settings
class Config:
    """Config settings."""

    script_dir: Path = ts.option(help="pricing script directory")


def get_config() -> Config:
    """Get config settings."""
    return ts.load_settings(Config, get_loaders("OES_PRICING_", ("pricing.yml",)))
