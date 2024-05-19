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
    redis_url: str | None = ts.option(default=None, help="url of a redis service")
    pricing_url: str = ts.option(
        default="http://pricing:8000", help="url of the pricing service"
    )
    currency: str = ts.option(default="USD", help="the currency to use")


def get_config() -> Config:
    """Get the config."""
    loaders = get_loaders("OES_CART_", ("cart.yml",))
    return ts.load_settings(Config, loaders)
