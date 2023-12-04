"""OAuth server module."""
import asyncio

from oauthlib.common import Request
from oauthlib.oauth2 import Server
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.credential_service import (
    CredentialService,
    create_new_refresh_token,
)
from oes.registration.auth.device_service import DeviceAuthService
from oes.registration.auth.oauth.device import (
    DeviceAuthorizationEndpoint,
    DeviceGrantType,
)
from oes.registration.auth.oauth.validator import CustomValidator, GrantType
from oes.registration.auth.scope import Scopes
from oes.registration.auth.token import AccessToken, RefreshToken
from oes.registration.auth.user import UserIdentity
from oes.registration.models.config import AuthConfig


class CustomServer(Server, DeviceAuthorizationEndpoint):
    """OAuth custom server."""

    _auth_config: AuthConfig
    _account_service: AccountService
    _credential_service: CredentialService
    _loop: asyncio.AbstractEventLoop

    def __init__(
        self,
        auth_config: AuthConfig,
        default_scope: Scopes,
        account_service: AccountService,
        credential_service: CredentialService,
        device_auth_service: DeviceAuthService,
        loop: asyncio.AbstractEventLoop,
    ):
        super().__init__(
            request_validator=CustomValidator(
                auth_config, default_scope, account_service, credential_service, loop
            ),
            token_generator=self._generate_access_token,
            refresh_token_generator=self._generate_refresh_token,
        )

        device_grant = DeviceGrantType(
            self.request_validator,
            loop,
            auth_config,
            account_service,
            device_auth_service,
        )

        DeviceAuthorizationEndpoint.__init__(self, device_grant)

        self._auth_config = auth_config
        self._account_service = account_service
        self._credential_service = credential_service
        self._loop = loop

        self.grant_types[GrantType.device_code.value] = device_grant

    def _generate_access_token(self, request: Request) -> str:
        access_token = AccessToken.create(
            account_id=request.user.id if request.user else None,
            scope=Scopes(request.scopes),
            email=request.user.email if request.user else None,
            client_id=request.client_id,
        )
        return access_token.encode(key=self._auth_config.signing_key)

    def _generate_refresh_token(self, request: Request) -> str:
        cur_token = request.refresh_token
        if isinstance(cur_token, RefreshToken):
            # Update the token
            refresh_token = cur_token.reissue_refresh_token()
        else:
            assert request.user is None or isinstance(request.user, UserIdentity)
            refresh_token = create_new_refresh_token(
                request.user,
                request.user.scope
                if request.user
                else None,  # TODO: check allowed scopes
            )

        request.refresh_token = refresh_token
        return refresh_token.encode(key=self._auth_config.signing_key)
