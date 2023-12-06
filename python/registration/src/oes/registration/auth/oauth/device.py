"""Device authorization grant type."""
from __future__ import annotations

import asyncio
import json
from datetime import timedelta

from oauthlib.common import Request
from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2.rfc6749 import BaseEndpoint, errors
from oauthlib.oauth2.rfc6749.grant_types.base import GrantTypeBase
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.device_service import DeviceAuthService, complete_device_auth
from oes.registration.auth.entities import DeviceAuthEntity
from oes.registration.auth.oauth.validator import GrantType
from oes.registration.auth.scope import Scopes
from oes.registration.models.config import AuthConfig
from oes.util import get_now

DEFAULT_AUTH_CODE_EXPIRATION_TIME = timedelta(minutes=3)


class DeviceAuthorizationEndpoint(BaseEndpoint):
    """Device authorization endpoint."""

    def __init__(self, grant: DeviceGrantType):
        super().__init__()
        self.device_grant = grant

    def create_device_authorization_response(
        self, uri: str, http_method, body, headers
    ) -> tuple[dict, bytes, int]:
        request = Request(uri, http_method, body, headers)
        try:
            return self.device_grant.create_device_authorization_response(request)
        except errors.OAuth2Error as e:
            return e.headers, e.json, e.status_code


class DeviceGrantType(GrantTypeBase):
    """Device grant type implementation."""

    request_validator: RequestValidator

    def __init__(
        self,
        request_validator: RequestValidator,
        loop: asyncio.AbstractEventLoop,
        auth_config: AuthConfig,
        account_service: AccountService,
        device_auth_service: DeviceAuthService,
        **kwargs,
    ):
        self._loop = loop
        self._auth_config = auth_config
        self._account_service = account_service
        self._auth_service = device_auth_service
        super().__init__(request_validator, **kwargs)

    def create_device_authorization_response(
        self, request: Request
    ) -> tuple[dict, bytes, int]:
        if not request.client_id:
            raise errors.MissingClientIdError(request=request)

        if not self.request_validator.validate_client_id(request.client_id, request):
            raise errors.InvalidClientIdError(request=request)

        self.validate_scopes(request)

        auth = asyncio.run_coroutine_threadsafe(
            self._create_auth_entity(request.client_id, Scopes(request.scopes)),
            self._loop,
        ).result()

        response_data = json.dumps(
            {
                "device_code": auth.device_code,
                "user_code": auth.user_code,
                "verification_uri": f"{self._auth_config.auth_base_url}"
                "/auth/authorize-device",
                "verification_uri_complete": f"{self._auth_config.auth_base_url}/auth"
                f"/authorize-device#user_code={auth.user_code}",
                "expires_in": DEFAULT_AUTH_CODE_EXPIRATION_TIME.total_seconds(),
            }
        )
        return self._get_default_headers(), response_data, 200

    def create_token_response(self, request: Request, token_handler):
        try:
            auth = self._validate_token_response(request)
        except errors.OAuth2Error as e:
            return e.headers, e.json, e.status_code

        token = token_handler.create_token(
            request, refresh_token=not auth.require_webauthn
        )

        self.request_validator.save_token(token, request)
        headers = self._get_default_headers()
        headers.update(self._create_cors_headers(request))
        return headers, json.dumps(token), 200

    def _validate_token_response(self, request: Request):
        if request.grant_type != GrantType.device_code:
            raise errors.UnsupportedGrantTypeError(request=request)

        if not getattr(request, "device_code", None):
            raise errors.InvalidRequestError(request=request)

        if self.request_validator.client_authentication_required(request):
            if not self.request_validator.authenticate_client(request):
                raise errors.InvalidClientError(request=request)
        elif not self.request_validator.authenticate_client_id(
            request.client_id, request
        ):
            raise errors.InvalidClientError(request=request)

        request.client_id = request.client_id or request.client.client_id

        self.validate_grant_type(request)

        auth = asyncio.run_coroutine_threadsafe(
            self._get_auth(request.device_code), self._loop
        ).result()

        if auth is None:
            raise errors.InvalidGrantError(request=request)
        elif not auth.is_valid():
            err = errors.InvalidGrantError(request=request)
            err.error = "expired_token"
            raise err
        elif not auth.account_id:
            err = errors.InvalidGrantError(request=request)
            err.error = "authorization_pending"
            raise err

        res = asyncio.run_coroutine_threadsafe(
            self._complete_auth(auth), self._loop
        ).result()

        if auth is None:
            raise errors.InvalidGrantError(request=request)

        request.user = res
        request.scopes = list(res.scope)

        return auth

    async def _create_auth_entity(
        self, client_id: str, scope: Scopes = Scopes()
    ) -> DeviceAuthEntity:
        entity = DeviceAuthEntity.create(
            client_id=client_id,
            scope=scope,
            date_expires=get_now() + DEFAULT_AUTH_CODE_EXPIRATION_TIME,
        )
        await self._auth_service.save_device_auth(entity)
        return entity

    async def _get_auth(self, device_code: str):
        return await self._auth_service.get_by_device_code(device_code)

    async def _complete_auth(self, auth: DeviceAuthEntity):
        return await complete_device_auth(
            auth, self._auth_service, self._account_service
        )
