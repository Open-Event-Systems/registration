"""oauthlib request validator module."""
import asyncio
from enum import Enum
from typing import Optional
from uuid import UUID

import jwt
from oauthlib.common import Request
from oauthlib.oauth2 import RequestValidator
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.credential_service import (
    CredentialService,
    create_refresh_token_entity,
    validate_refresh_token,
)
from oes.registration.auth.oauth.client import Client, get_js_client
from oes.registration.auth.scope import Scope, Scopes
from oes.registration.auth.token import AccessToken, RefreshToken
from oes.registration.auth.user import UserIdentity
from oes.registration.models.config import AuthConfig


class GrantType(str, Enum):
    """OAuth grant types."""

    refresh_token = "refresh_token"
    device_code = "urn:ietf:params:oauth:grant-type:device_code"


class CustomValidator(RequestValidator):
    """Custom OAuth validator."""

    _auth_config: AuthConfig
    _account_service: AccountService
    _credential_service: CredentialService
    _clients: dict[str, Client]
    _loop: asyncio.AbstractEventLoop

    def __init__(
        self,
        auth_config: AuthConfig,
        default_scope: Scopes,
        account_service: AccountService,
        credential_service: CredentialService,
        loop: asyncio.AbstractEventLoop,
    ):
        self._auth_config = auth_config
        self._default_scope = default_scope
        self._account_service = account_service
        self._credential_service = credential_service
        self._loop = loop

        js_client = get_js_client(auth_config)
        self._clients = {
            js_client.id: js_client,
        }

    def validate_client_id(
        self, client_id: str, request: Request, *args, **kwargs
    ) -> bool:
        client = self._clients.get(client_id)
        if client is None:
            return False
        request.client = client
        return True

    def validate_redirect_uri(
        self, client_id: str, redirect_uri: str, request: Request, *args, **kwargs
    ) -> bool:
        client = self._clients.get(client_id)
        return client is not None and redirect_uri in client.redirect_uris

    def get_default_redirect_uri(
        self, client_id: str, request: Request, *args, **kwargs
    ):
        return None

    def validate_scopes(
        self,
        client_id: str,
        scopes: list[str],
        client: Client,
        request: Request,
        *args,
        **kwargs
    ) -> bool:
        return all(s in Scope.__members__.values() for s in scopes)

    def get_default_scopes(
        self, client_id: str, request: Request, *args, **kwargs
    ) -> list[str]:
        return sorted(self._default_scope)

    def validate_response_type(
        self,
        client_id: str,
        response_type: str,
        client: Client,
        request: Request,
        *args,
        **kwargs
    ) -> bool:
        return response_type == "code"  # TODO

    def client_authentication_required(self, request: Request, *args, **kwargs) -> bool:
        return False

    def authenticate_client_id(
        self, client_id: str, request: Request, *args, **kwargs
    ) -> bool:
        client = self._clients.get(client_id)
        if client is None:
            return False
        request.client = client
        return True

    def validate_grant_type(
        self,
        client_id: str,
        grant_type: str,
        client: Client,
        request: Request,
        *args,
        **kwargs
    ) -> bool:
        # TODO: check setting for each client
        return grant_type in GrantType.__members__.values()

    def save_bearer_token(
        self, token: dict, request: Request, *args, **kwargs
    ) -> Optional[str]:
        if isinstance(request.refresh_token, RefreshToken) and "refresh_token" in token:
            entity = create_refresh_token_entity(request.refresh_token)
            fut = asyncio.run_coroutine_threadsafe(
                self._credential_service.update_credential(entity), self._loop
            )
            fut.result()
            token["email"] = request.refresh_token.email
            token["account_id"] = (
                str(UUID(request.refresh_token.sub))
                if request.refresh_token.sub
                else None
            )
        return None

    def validate_bearer_token(
        self, token: str, scopes: list[str], request: Request
    ) -> bool:
        access_token = self._validate_token(token)
        if access_token is None:
            return False

        # At least one of the resource's required scopes must be present in the token's
        # scopes
        if not any(s in access_token.scope for s in scopes):
            return False

        client = self._clients.get(access_token.azp) if access_token.azp else None
        if client is not None:
            request.client = client

        request.scopes = list(access_token.scope)
        request.access_token = access_token
        request.user = UserIdentity(
            id=UUID(access_token.sub) if access_token.sub else None,
            email=access_token.email,
            scope=access_token.scope,
        )

        return True

    def validate_refresh_token(
        self, refresh_token: str, client: Client, request: Request, *args, **kwargs
    ) -> bool:
        fut = asyncio.run_coroutine_threadsafe(
            validate_refresh_token(
                refresh_token,
                account_service=self._account_service,
                key=self._auth_config.signing_key,
            ),
            self._loop,
        )
        refresh_token_obj = fut.result()
        if refresh_token_obj is None:
            return False

        # Check azp/client ID
        if refresh_token_obj.azp is not None and refresh_token_obj.azp != client.id:
            return False

        request.user = UserIdentity(
            id=UUID(refresh_token_obj.sub) if refresh_token_obj.sub else None,
            email=refresh_token_obj.email,
            scope=refresh_token_obj.scope,
        )
        request.refresh_token = refresh_token_obj
        return True

    def get_original_scopes(
        self, refresh_token: str, request: Request, *args, **kwargs
    ) -> list[str]:
        if isinstance(request.refresh_token, RefreshToken):
            return list(request.refresh_token.scope)
        else:
            return []

    def is_origin_allowed(
        self, client_id: str, origin: str, request: Request, *args, **kwargs
    ) -> bool:
        return (
            origin in self._auth_config.allowed_origins
            or "*" in self._auth_config.allowed_origins
        )

    def _validate_token(self, token: str) -> Optional[AccessToken]:
        try:
            return AccessToken.decode(token, key=self._auth_config.signing_key)
        except jwt.InvalidTokenError:
            return None
