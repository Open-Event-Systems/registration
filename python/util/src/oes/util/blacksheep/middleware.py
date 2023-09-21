"""Middlewares module."""
from collections.abc import Iterable
from ipaddress import ip_network
from typing import Union

from blacksheep import Application
from blacksheep.server.remotes.forwarding import XForwardedHeadersMiddleware


def configure_forwarded_headers(app: Application):
    """Configure an app to accept ``X-Forwarded`` headers.

    References:
        https://www.neoteroi.dev/blacksheep/remotes/#handling-x-forwarded-headers
    """
    app.middlewares.insert(
        0,
        XForwardedHeadersMiddleware(
            known_networks=(ip_network("0.0.0.0/0"), ip_network("::/0"))
        ),
    )


def configure_cors(
    app: Application,
    *,
    allow_origins: Union[str, Iterable[str], None] = None,
    allow_methods: Union[str, Iterable[str]] = "*",
    allow_headers: Union[str, Iterable[str], None] = None,
    max_age: int = 600,
):
    """Configure an app to set CORS headers."""
    app.use_cors(
        allow_origins=allow_origins,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=max_age,
    )
