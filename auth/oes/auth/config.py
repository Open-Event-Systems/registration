"""Config."""

import typed_settings as ts
from oes.utils.config import get_loaders
from sqlalchemy import URL, make_url


@ts.settings
class Config:
    """Config object."""

    token_secret: ts.SecretStr = ts.secret(help="the secret for signing tokens")
    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///auth"),
        converter=lambda v: make_url(v),
        help="the database URL",
    )
    amqp_url: str = ts.option(
        default="amqp://guest:guest@localhost/", help="the AMQP server URL"
    )
    disable_auth: bool = ts.option(default=False, help="disable auth")

    origin: str = ts.option(
        default="http://localhost:8080", help="the domain of the web UI"
    )
    name: str = ts.option(default="Registration", help="the name of the service")


def get_config() -> Config:
    """Load the config."""
    loaders = get_loaders("OES_AUTH_SERVICE_", ("auth.yml",))
    return ts.load_settings(Config, loaders)
