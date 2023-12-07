"""Email auth views."""
import re

from attr import frozen
from blacksheep import HTTPException, Response
from blacksheep.exceptions import Forbidden
from blacksheep.server.openapi.common import ResponseInfo
from oes.registration.app import app
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.email_auth_service import EmailAuthService, send_auth_code
from oes.registration.auth.token import AccessToken, TokenResponse
from oes.registration.auth.user import User
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper
from oes.registration.models.config import Config
from oes.registration.views.parameters import AttrsBody
from oes.util import get_now
from sqlalchemy.ext.asyncio import AsyncSession


@frozen
class EmailVerificationBody:
    """An email verification request."""

    email: str


@frozen
class EmailVerificationCodeBody:
    """An email verification code."""

    email: str
    code: str


@app.router.post("/auth/email/send")
@docs(
    responses={
        204: ResponseInfo(
            "The email was sent.",
        ),
    },
    tags=["Account"],
)
@transaction
async def send_email_verification(
    body: AttrsBody[EmailVerificationBody],
    email_auth_service: EmailAuthService,
    config: Config,
    user: User,
) -> Response:
    """Send an email verification code."""
    if user.email:
        raise Forbidden

    email = body.value.email.strip()
    if not re.match(r"^.+@.+\..+$", email):
        raise HTTPException(422, "Invalid email")
    await send_auth_code(email_auth_service, config.hooks, email)
    return Response(204)


@app.router.post("/auth/email/verify")
@docs_helper(
    response_type=TokenResponse,
    response_summary="An updated access token.",
    tags=["Account"],
)
async def verify_email(
    body: AttrsBody[EmailVerificationCodeBody],
    email_auth_service: EmailAuthService,
    account_service: AccountService,
    db: AsyncSession,
    user: User,
    config: Config,
) -> TokenResponse:
    """Verify an email address."""
    email = body.value.email.strip()
    code = re.sub(r"[^a-zA-Z0-9]+", "", body.value.code)
    entity = await email_auth_service.get_auth_code_for_email(email)
    if not entity or not entity.get_is_usable():
        raise Forbidden
    elif code != entity.code:
        entity.attempts += 1
        await db.commit()
        raise Forbidden
    else:
        account = await account_service.get_account(user.id, lock=True)
        if not account or account.email:
            raise Forbidden

        account.email = entity.email

        now = get_now(seconds_only=True)
        new_access_token = AccessToken.create(
            account_id=user.id,
            scope=user.scope,
            email=entity.email,
            client_id=user.client_id,
            expiration_date=user.expiration_date,
        )
        expires_in = int((new_access_token.exp - now).total_seconds())

        await email_auth_service.delete_code(entity)

        await db.commit()
        return TokenResponse.create(
            access_token=new_access_token,
            scope=new_access_token.scope,
            expires_in=expires_in,
            key=config.auth.signing_key,
        )
