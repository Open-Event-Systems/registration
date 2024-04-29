"""Config module."""

import typed_settings as ts
from oes.utils.config import get_loaders
from sqlalchemy import URL, make_url


@ts.settings
class Config:
    """Config settings."""

    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///cart"),
        converter=lambda v: make_url(v),
        help="the database URL",
    )

    salt: str = ts.option(default="changeit", help="random salt value")


def get_config() -> Config:
    """Get the config."""
    loaders = get_loaders("OES_CART_")
    return ts.load_settings(Config, loaders)
