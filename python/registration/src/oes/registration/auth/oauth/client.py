"""Client module."""
from collections.abc import Sequence

from attr import field, frozen
from oes.registration.models.config import AuthConfig

JS_CLIENT_ID = "oes"
"""The main JS client ID."""


@frozen(kw_only=True)
class Client:
    """OAuth client."""

    id: str
    """The client ID."""

    redirect_uris: Sequence[str] = field(converter=tuple)
    """Allowed redirect URIs."""

    @property
    def client_id(self) -> str:
        """The client ID."""
        return self.id


def get_js_client(auth_config: AuthConfig) -> Client:
    """Get the :class:`Client` for the main JS client."""
    redirect_uris = []
    for origin in auth_config.allowed_auth_origins:
        if origin != "*":
            redirect_uris.append(f"{origin}/auth/redirect")  # TODO

    return Client(id=JS_CLIENT_ID, redirect_uris=redirect_uris)
