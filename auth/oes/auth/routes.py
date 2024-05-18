"""Routes."""

import nanoid
import orjson
from attrs import frozen
from oes.auth.config import Config
from oes.auth.service import AuthService, RefreshTokenService
from oes.auth.token import TokenError
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, HTTPResponse, Request, Unauthorized

routes = Blueprint("auth")


@frozen
class CreateRefreshTokenRequest:
    """Request to create a new refresh token."""

    account_id: str | None = None
    email: str | None = None


@routes.get("/auth/validate")
async def validate_token(request: Request, auth_service: AuthService) -> HTTPResponse:
    """Validate a token."""
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


_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
