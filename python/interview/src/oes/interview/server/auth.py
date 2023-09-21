"""Auth module."""
from typing import Optional

from blacksheep import Request
from guardpost import Identity, Policy
from guardpost.asynchronous.authentication import (
    AuthenticationHandler,
    AuthenticationStrategy,
)
from guardpost.asynchronous.authorization import AuthorizationStrategy
from guardpost.common import AuthenticatedRequirement
from typed_settings import Secret

AUTHENTICATED = "authenticated"
"""Authenticated policy."""

_policy = Policy(AUTHENTICATED, AuthenticatedRequirement())

authentication = AuthenticationStrategy()
authorization = AuthorizationStrategy()

authorization.add(_policy)
authorization.default_policy = _policy


class APIKeyHandler(AuthenticationHandler):
    def __init__(self, api_key: Secret[str]):
        self._api_key = api_key

    async def authenticate(self, context: Request) -> Optional[Identity]:
        header = context.get_first_header(b"Authorization") or b""
        typ, _, key = header.partition(b" ")
        key_str = key.decode()

        if typ.lower() == b"bearer" and key_str == self._api_key.get_secret_value():
            identity = Identity({}, "api_key")
            context.identity = identity
            return identity
        else:
            context.identity = None
            return None
