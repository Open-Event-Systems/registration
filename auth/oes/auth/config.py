"""Config."""

from collections.abc import Mapping
from typing import Any, cast

import typed_settings as ts
from oes.auth.auth import Scopes
from oes.utils.config import get_loaders
from sqlalchemy import URL, make_url


@ts.settings
class RoleConfig:
    """Role config."""

    title: str = ts.option(help="role title")
    scope: Scopes = ts.option(help="role scope")

    def can_use(self, other_scope: Scopes) -> bool:
        """Return whether a user with the given scope can see/set this role."""
        return all(s in other_scope for s in self.scope)


@ts.settings
class Config:
    """Config object."""

    token_secret: ts.SecretStr = ts.secret(help="the secret for signing tokens")
    db_url: URL = ts.option(
        default=make_url("postgresql+asyncpg:///auth"),
        help="the database URL",
    )
    amqp_url: str = ts.option(
        default="amqp://guest:guest@localhost/", help="the AMQP server URL"
    )
    disable_auth: bool = ts.option(default=False, help="disable auth")
    allowed_origins: list[str] = ts.option(factory=list, help="list of allowed origins")
    roles: Mapping[str, RoleConfig] = ts.option(factory=dict, help="role config")


def get_config() -> Config:
    """Load the config."""
    loaders = get_loaders("OES_AUTH_SERVICE_", ("auth.yml",))
    return ts.load_settings(Config, loaders, converter=cast(Any, _converter))


_converter = ts.converters.get_default_cattrs_converter()
_converter.register_structure_hook(URL, lambda v, t: make_url(v))
