"""WebAuthn views."""

from attr import frozen
from blacksheep import Request, Response, allow_anonymous
from blacksheep.exceptions import Forbidden, NotFound
from loguru import logger
from oes.registration.app import app
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.credential_service import (
    CredentialService,
    create_new_refresh_token,
    create_refresh_token_entity,
)
from oes.registration.auth.models import CredentialType
from oes.registration.auth.oauth.client import JS_CLIENT_ID
from oes.registration.auth.scope import Scopes
from oes.registration.auth.token import WEBAUTHN_REFRESH_TOKEN_LIFETIME, TokenResponse
from oes.registration.auth.user import User, UserIdentity
from oes.registration.auth.webauthn import (
    WebAuthnAuthenticationChallenge,
    WebAuthnError,
    WebAuthnRegistrationChallenge,
    add_webauthn_credential,
    validate_webauthn_authentication,
    validate_webauthn_registration,
)
from oes.registration.database import transaction
from oes.registration.docs import docs_helper
from oes.registration.models.config import Config
from oes.registration.util import check_not_found, get_now, get_origin, origin_to_rp_id
from oes.util.blacksheep import FromAttrs


@frozen
class WebAuthnChallengeResponse:
    """A WebAuthn challenge."""

    challenge: str
    options: dict


@frozen
class WebAuthnChallengeResult:
    """A completed WebAuthn challenge."""

    challenge: str
    result: str


@app.router.get("/auth/webauthn/register")
@docs_helper(
    response_type=WebAuthnChallengeResponse,
    response_summary="The registration challenge",
    tags=["Account"],
)
async def get_webauthn_registration_challenge(
    request: Request,
    config: Config,
    user: User,
) -> WebAuthnChallengeResponse:
    """Get a WebAuthn registration challenge."""
    origin = get_origin(request)

    if origin not in config.auth.allowed_auth_origins:
        raise Forbidden

    challenge, opts = WebAuthnRegistrationChallenge.create(
        rp_id=origin_to_rp_id(origin),
        rp_name=config.auth.name,
        account_id=user.id,
        user_name=user.email,
    )

    return WebAuthnChallengeResponse(
        challenge=challenge.encode(key=config.auth.signing_key),
        options=opts.dict(by_alias=True, exclude_none=True),
    )


@app.router.post("/auth/webauthn/register")
@docs_helper(
    response_summary="The token response for the new account",
    tags=["Account"],
)
@transaction
async def complete_webauthn_registration(
    request: Request,
    body: FromAttrs[WebAuthnChallengeResult],
    config: Config,
    account_service: AccountService,
    credential_service: CredentialService,
) -> Response:
    """Complete a WebAuthn registration."""
    origin = get_origin(request)

    try:
        credential_entity = validate_webauthn_registration(
            body.value.challenge,
            body.value.result,
            origin,
            config.auth,
        )

        await add_webauthn_credential(
            credential_entity, account_service, credential_service
        )
    except WebAuthnError as e:
        logger.debug(f"WebAuthn registration failed: {e}")
        raise Forbidden

    # TODO: clients with reduced scope can register a credential and use that to upgrade
    #   to the user's full scope. only first-party clients should be able to use this,
    #   currently only the origin is checked.
    return Response(204)


@allow_anonymous()
@app.router.get("/auth/webauthn/authenticate/{credential_id}")
@docs_helper(
    response_type=WebAuthnChallengeResponse,
    response_summary="The authentication challenge",
    tags=["Account"],
)
async def get_webauthn_authentication_challenge(
    credential_id: str,
    request: Request,
    credential_service: CredentialService,
    config: Config,
) -> WebAuthnChallengeResponse:
    """Get a WebAuthn authentication challenge."""
    origin = get_origin(request)
    if origin not in config.auth.allowed_auth_origins:
        raise Forbidden

    entity = check_not_found(
        await credential_service.get_credential(credential_id.rstrip("="))
    )
    if entity.type != CredentialType.webauthn:
        raise NotFound

    challenge, opts = WebAuthnAuthenticationChallenge.create(
        rp_id=origin_to_rp_id(origin),
        credential_id=entity.id,
    )

    return WebAuthnChallengeResponse(
        challenge=challenge.encode(key=config.auth.signing_key),
        options=opts.dict(by_alias=True, exclude_none=True),
    )


@allow_anonymous()
@app.router.post("/auth/webauthn/authenticate")
@docs_helper(
    response_type=TokenResponse,
    response_summary="The token response",
    tags=["Account"],
)
@transaction
async def complete_webauthn_authentication(
    request: Request,
    body: FromAttrs[WebAuthnChallengeResult],
    account_service: AccountService,
    credential_service: CredentialService,
    config: Config,
) -> TokenResponse:
    """Complete a WebAuthn authentication challenge."""
    origin = get_origin(request)

    try:
        account_id = await validate_webauthn_authentication(
            challenge_data=body.value.challenge,
            response_data=body.value.result,
            origin=origin,
            credential_service=credential_service,
            auth_config=config.auth,
        )
    except WebAuthnError as e:
        logger.debug(f"WebAuthn authentication failed: {e}")
        raise Forbidden

    account = check_not_found(
        await account_service.get_account(account_id, with_credentials=True)
    )
    user = UserIdentity(
        id=account.id,
        email=account.email,
        scope=Scopes(account.scope),
        client_id=JS_CLIENT_ID,
    )

    now = get_now(seconds_only=True)
    exp = now + WEBAUTHN_REFRESH_TOKEN_LIFETIME

    refresh_token = create_new_refresh_token(
        user,
        expiration_date=exp,
    )
    refresh_token_entity = create_refresh_token_entity(refresh_token)
    await credential_service.create_credential(refresh_token_entity)
    access_token = refresh_token.create_access_token()

    return TokenResponse.create(
        access_token=access_token,
        refresh_token=refresh_token,
        scope=access_token.scope,
        expires_in=int(WEBAUTHN_REFRESH_TOKEN_LIFETIME.total_seconds()),
        key=config.auth.signing_key,
    )
