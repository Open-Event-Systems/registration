"""Routes."""

import re
from datetime import datetime

import orjson
from attrs import frozen
from email_validator import EmailNotValidError, validate_email
from oes.auth.auth import AuthRepo, AuthService, Scope
from oes.auth.config import Config
from oes.auth.email import EmailAuthService
from oes.auth.mq import MQService
from oes.auth.policy import is_allowed
from oes.auth.service import AccessTokenService, RefreshTokenService
from oes.auth.token import AccessToken, RefreshToken, RefreshTokenRepo, TokenError
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, Forbidden, HTTPResponse, Request, Unauthorized, json
from sanic.exceptions import HTTPException

routes = Blueprint("auth")


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
    request: Request, config: Config, access_token_service: AccessTokenService
) -> HTTPResponse:
    """Validate a token."""
    if config.disable_auth:
        return HTTPResponse(status=204)

    # return 204 for options
    if request.headers.get("x-original-method", "") == "OPTIONS":
        return HTTPResponse(status=204)

    orig_uri = request.headers.get("x-original-uri", "")

    token = _validate_token(request, access_token_service)

    response_headers = {}

    if token.sub:
        response_headers["x-account-id"] = token.sub

    if token.email:
        response_headers["x-email"] = token.email

    response_headers["x-scope"] = list(token.scope)

    allowed = await is_allowed(request.method, orig_uri, token.scope)

    if not allowed:
        raise Forbidden

    return HTTPResponse(status=204, headers=response_headers)


@routes.get("/auth/info")
async def read_info(request: Request, auth_service: AccessTokenService) -> HTTPResponse:
    """Read auth info."""
    header = request.headers.get("Authorization", "")
    token = auth_service.validate_token(header)
    if token is None:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})

    return json(
        {
            "account_id": token.sub,
            "email": token.email,
            "scope": str(token.scope),
        }
    )


@routes.post("/auth/create")
async def create_auth(
    request: Request,
    auth_service: AuthService,
    refresh_token_service: RefreshTokenService,
    config: Config,
) -> HTTPResponse:
    """Create a guest authorization."""
    async with transaction():
        auth = auth_service.create_auth(
            scope=(Scope.selfservice, Scope.cart), path_length=0
        )
        refresh_token = await refresh_token_service.create(auth)
        access_token = refresh_token.make_access_token(now=refresh_token.date_created)
        return _make_token_response(access_token, refresh_token, config)


@routes.post("/auth/token")
async def refresh_token(
    request: Request,
    refresh_token_service: RefreshTokenService,
    config: Config,
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
            updated = await refresh_token_service.refresh(refresh_token_str)
        except TokenError:
            raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})
        access_token = updated.make_access_token(now=updated.date_created)
        return _make_token_response(access_token, updated, config)


@routes.post("/auth/email")
async def start_email_auth(
    request: Request,
    service: EmailAuthService,
    access_token_service: AccessTokenService,
    body: CattrsBody,
) -> HTTPResponse:
    """Start email auth."""
    req = await body(StartEmailAuthRequest)
    token = _validate_token(request, access_token_service)
    if token.email:
        raise Forbidden
    email = req.email.strip()
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        raise UnprocessableEntity
    await service.send(email)
    return HTTPResponse(status=204)


@routes.post("/auth/email/verify")
async def complete_email_auth(
    request: Request,
    service: EmailAuthService,
    auth_repo: AuthRepo,
    refresh_token_service: RefreshTokenService,
    access_token_service: AccessTokenService,
    config: Config,
    body: CattrsBody,
) -> HTTPResponse:
    """Complete email auth."""
    req = await body(CompleteEmailAuthRequest)
    token = _validate_token(request, access_token_service)
    if token.email:
        raise Forbidden
    email = req.email.strip()
    code = re.sub(r"[. -]", "", req.code)

    async with transaction():
        # TODO: need to move a lot of business logic out of here
        auth = await auth_repo.get(token.sub, lock=True)
        if not auth or auth.email:
            raise Forbidden
        res = await service.verify(email, code)
        if not res:
            raise Forbidden

        auth.email = email
        refresh_token = await refresh_token_service.create(auth)
        access_token = refresh_token.make_access_token(now=refresh_token.date_created)
        return _make_token_response(access_token, refresh_token, config)


def _validate_token(
    request: Request, access_token_service: AccessTokenService
) -> AccessToken:
    header = request.headers.get("Authorization", "")
    token = access_token_service.validate_token(header)
    if token is None:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})
    return token


def _make_token_response(
    access_token: AccessToken, refresh_token: RefreshToken | None, config: Config
) -> HTTPResponse:
    iat = refresh_token.date_created if refresh_token else datetime.now().astimezone()
    resp_data = {
        "access_token": access_token.encode(key=config.token_secret),
        "token_type": "Bearer",
        "scope": str(access_token.scope),
        "account_id": access_token.acc,
        "email": access_token.email,
        "expires_in": int((access_token.exp - iat).total_seconds()),
        "refresh_token": (
            f"{refresh_token.auth_id}-{refresh_token.token}" if refresh_token else None
        ),
    }
    return HTTPResponse(orjson.dumps(resp_data), content_type="application/json")


@routes.get("/_healthcheck")
async def healthcheck(
    request: Request, repo: RefreshTokenRepo, message_queue: MQService
) -> HTTPResponse:
    """Health check endpoint."""
    await repo.get("")
    if not message_queue.ready:
        return HTTPResponse(status=503)
    return HTTPResponse(status=204)
