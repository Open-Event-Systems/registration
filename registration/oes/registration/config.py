"""Config."""

import typed_settings as ts
from oes.utils.config import get_loaders
from sqlalchemy import URL, make_url


@ts.settings
class Config:
    """Config object."""

    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///registration"),
        converter=lambda v: make_url(v),
        help="the database URL",
    )


def get_config() -> Config:
    """Load the config."""
    loaders = get_loaders("OES_REGISTRATION_SERVICE_")
    return ts.load_settings(Config, loaders)
