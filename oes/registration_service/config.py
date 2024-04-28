"""Config."""

import typed_settings as ts

from oes.utils.config import get_loaders


@ts.settings
class DBConfig:
    """Database config."""

    url: str = ts.option(
        default="postgresql+asyncpg:///registration", help="the database URL"
    )


@ts.settings
class Config:
    """Config object."""

    database: DBConfig = DBConfig()


def get_config() -> Config:
    """Load the config."""
    loaders = get_loaders("OES_")
    return ts.load_settings(Config, loaders)
