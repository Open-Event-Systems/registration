"""Client module."""
from collections.abc import Sequence

from attr import field, frozen
from oes.registration.models.config import AuthConfig

JS_CLIENT_ID = "oes"
"""The main JS client ID."""

KIOSK_CLIENT_ID = "oes.kiosk"
"""The kiosk client ID."""

CLIENTS = {
    JS_CLIENT_ID: "Registration",
    KIOSK_CLIENT_ID: "Registration Kiosk",
}


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


def get_clients(auth_config: AuthConfig) -> dict[str, Client]:
    """Get the :class:`Client` objects."""
    redirect_uris = []
    for origin in auth_config.allowed_auth_origins:
        if origin != "*":
            redirect_uris.append(f"{origin}/auth/redirect")  # TODO
    return {
        k: Client(id=k, redirect_uris=tuple(redirect_uris)) for k, v in CLIENTS.items()
    }
