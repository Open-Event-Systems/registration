"""General auth views."""
from typing import Optional
from uuid import UUID

from attr import frozen
from blacksheep import FromForm, allow_anonymous
from blacksheep.exceptions import Forbidden
from blacksheep.server.openapi.common import ContentInfo, RequestBodyInfo, ResponseInfo
from oes.registration.app import app
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.credential_service import (
    create_new_refresh_token,
    create_refresh_token_entity,
)
from oes.registration.auth.models import CredentialType
from oes.registration.auth.oauth.client import CLIENTS, JS_CLIENT_ID
from oes.registration.auth.scope import get_default_scopes
from oes.registration.auth.token import (
    DEFAULT_REFRESH_TOKEN_LIFETIME,
    GUEST_INITIAL_ACCESS_TOKEN_LIFETIME,
    WEBAUTHN_REFRESH_TOKEN_LIFETIME,
    AccessToken,
    TokenResponse,
)
from oes.registration.auth.user import User
from oes.registration.config import CommandLineConfig
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper, serialize
from oes.registration.models.config import Config
from oes.util import get_now


@frozen
class AccountInfoResponse:
    """Account info."""

    id: Optional[UUID] = None
    email: Optional[str] = None
    scope: str = ""


@app.router.get("/auth/account")
@docs_helper(
    response_type=AccountInfoResponse,
    response_summary="The account information",
    tags=["Account"],
)
async def get_account_info(user: User) -> AccountInfoResponse:
    """Get the current account info."""
    return AccountInfoResponse(
        id=user.id,
        email=user.email,
        scope=str(user.scope),
    )


@allow_anonymous()
@app.router.post("/auth/account/create")
@docs(
    request_body=RequestBodyInfo(examples={"Default Client": {"client_id": "oes"}}),
    responses={
        200: ResponseInfo(
            "The token response for the new account",
            content=[ContentInfo(TokenResponse)],
        )
    },
    tags=["Account"],
)
@serialize(TokenResponse)
@transaction
async def new_account_endpoint(
    form: FromForm,
    account_service: AccountService,
    config: Config,
    cmd_config: CommandLineConfig,
) -> TokenResponse:
    """Create a new account, without credentials."""
    client_id = form.value.get("client_id", JS_CLIENT_ID)
    client = CLIENTS.get(client_id)
    # TODO: only first-party clients should be allowed
    if not client:
        raise Forbidden

    scope = get_default_scopes(cmd_config)

    new_account = await account_service.create_account(None, scope=scope)

    now = get_now(seconds_only=True)
    exp = now + GUEST_INITIAL_ACCESS_TOKEN_LIFETIME
    access_token = AccessToken.create(
        new_account.id, scope=scope, client_id=client_id, expiration_date=exp
    )
    expires_in = int((access_token.exp - now).total_seconds())

    return TokenResponse.create(
        access_token=access_token,
        scope=access_token.scope,
        expires_in=expires_in,
        key=config.auth.signing_key,
    )


@app.router.post("/auth/refresh-token")
@docs_helper(
    response_type=TokenResponse,
    response_summary="The token response",
    tags=["Account"],
)
@transaction
async def get_initial_refresh_token(
    account_service: AccountService,
    user: User,
    config: Config,
) -> TokenResponse:
    """Get an initial refresh token."""
    account = await account_service.get_account(
        user.id, lock=True, with_credentials=True
    )
    if not account:
        raise Forbidden

    if any(c.type == CredentialType.refresh_token for c in account.credentials):
        raise Forbidden

    if any(c.type == CredentialType.webauthn for c in account.credentials):
        dur = WEBAUTHN_REFRESH_TOKEN_LIFETIME
    else:
        dur = DEFAULT_REFRESH_TOKEN_LIFETIME

    now = get_now(seconds_only=True)
    exp = now + dur
    refresh_token = create_new_refresh_token(
        user, scope=user.scope, expiration_date=exp
    )
    entity = create_refresh_token_entity(refresh_token)
    account.credentials.append(entity)

    access_token = refresh_token.create_access_token()
    expires_in = int((access_token.exp - now).total_seconds())
    return TokenResponse.create(
        access_token=access_token,
        refresh_token=refresh_token,
        scope=access_token.scope,
        expires_in=expires_in,
        key=config.auth.signing_key,
    )
