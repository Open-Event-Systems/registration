"""Config."""

from typing import Any, cast

import typed_settings as ts
from oes.utils.config import get_loaders
from sqlalchemy import URL, make_url


@ts.settings
class Config:
    """Config object."""

    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///registration"),
        help="the database URL",
    )
    amqp_url: str = ts.option(
        default="amqp://guest:guest@localhost/", help="the AMQP server URL"
    )


def get_config() -> Config:
    """Load the config."""
    loaders = get_loaders("OES_REGISTRATION_SERVICE_", ("registration.yml",))
    return ts.load_settings(Config, loaders, converter=cast(Any, _converter))


_converter = ts.converters.get_default_cattrs_converter()
_converter.register_structure_hook(URL, lambda v, t: make_url(v))
