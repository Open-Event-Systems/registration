"""Routes."""

import re

import nanoid
import orjson
from attrs import frozen
from email_validator import validate_email
from oes.auth.config import Config
from oes.auth.email import EmailAuthService
from oes.auth.service import AuthService, RefreshTokenService
from oes.auth.token import TokenError
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, Forbidden, HTTPResponse, Request, Unauthorized, json
from sanic.exceptions import HTTPException

routes = Blueprint("auth")


@frozen
class CreateRefreshTokenRequest:
    """Request to create a new refresh token."""

    account_id: str | None = None
    email: str | None = None


@frozen
class StartEmailAuthRequest:
    """Request to start email auth."""

    email: str


@frozen
class CompleteEmailAuthRequest:
    """Request to complete email auth."""

    email: str
    code: str


class UnprocessableEntity(HTTPException):
    """Unprocessable entity."""

    status_code = 422
    quiet = True


@routes.get("/auth/validate")
async def validate_token(
    request: Request, config: Config, auth_service: AuthService
) -> HTTPResponse:
    """Validate a token."""
    if config.disable_auth:
        return HTTPResponse(status=204)

    header = request.headers.get("Authorization", "")
    token = auth_service.validate_token(header)
    if token is None:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})

    response_headers = {}

    if token.sub:
        response_headers["x-account-id"] = token.sub

    if token.email:
        response_headers["x-email"] = token.email

    return HTTPResponse(status=204, headers=response_headers)


@routes.post("/auth/create")
async def create_refresh_token(
    request: Request, service: RefreshTokenService, config: Config, body: CattrsBody
) -> HTTPResponse:
    """Create a new refresh token."""
    req = await body(CreateRefreshTokenRequest)
    # TODO: this endpoint should be anonymous accounts only
    account_id = (
        req.account_id
        if req.account_id
        else nanoid.generate(_alphabet, 14) if not req.email else None
    )

    async with transaction():
        refresh_token = await service.create(account_id, req.email)
        access_token = refresh_token.make_access_token(now=refresh_token.date_issued)
        token_response = {
            "access_token": access_token.encode(key=config.token_secret),
            "token_type": "Bearer",
            "expires_in": int(
                (access_token.exp - refresh_token.date_issued).total_seconds()
            ),
            "refresh_token": f"{refresh_token.id}-{refresh_token.token}",
        }
        return HTTPResponse(
            orjson.dumps(token_response), content_type="application/json"
        )


@routes.post("/auth/token")
async def refresh_token(
    request: Request, service: RefreshTokenService, config: Config, body: CattrsBody
) -> HTTPResponse:
    """Create a new refresh token."""
    form = request.form
    if not form:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})

    grant_type = form.get("grant_type")
    refresh_token_str = form.get("refresh_token")

    if grant_type != "refresh_token" or not refresh_token_str:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})

    async with transaction():
        try:
            updated = await service.refresh(refresh_token_str)
        except TokenError:
            raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})
        access_token = updated.make_access_token(now=updated.date_issued)
        token_response = {
            "access_token": access_token.encode(key=config.token_secret),
            "token_type": "Bearer",
            "expires_in": int((access_token.exp - updated.date_issued).total_seconds()),
            "refresh_token": f"{updated.id}-{updated.token}",
        }
        return HTTPResponse(
            orjson.dumps(token_response), content_type="application/json"
        )


@routes.post("/auth/email")
async def start_email_auth(
    request: Request, service: EmailAuthService, body: CattrsBody
) -> HTTPResponse:
    """Start email auth."""
    req = await body(StartEmailAuthRequest)
    email = req.email.strip()
    if not validate_email(email, check_deliverability=False):
        raise UnprocessableEntity
    await service.send(email)
    return HTTPResponse(status=204)


@routes.post("/auth/email/verify")
async def complete_email_auth(
    request: Request,
    service: EmailAuthService,
    refresh_token_service: RefreshTokenService,
    config: Config,
    body: CattrsBody,
) -> HTTPResponse:
    """Complete email auth."""
    req = await body(CompleteEmailAuthRequest)
    email = req.email.strip()
    code = re.sub(r"[. -]", "", req.code)
    res = await service.verify(req.email.strip(), code)
    if not res:
        raise Forbidden
    async with transaction():
        refresh_token = await refresh_token_service.create(email=email)
        access_token = refresh_token.make_access_token(now=refresh_token.date_issued)
        token_response = {
            "access_token": access_token.encode(key=config.token_secret),
            "token_type": "Bearer",
            "expires_in": int(
                (access_token.exp - refresh_token.date_issued).total_seconds()
            ),
            "refresh_token": f"{refresh_token.id}-{refresh_token.token}",
        }
    return json(token_response)


_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
