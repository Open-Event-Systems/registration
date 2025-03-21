"""Routes."""

import re
from datetime import datetime

import orjson
from attrs import frozen
from email_validator import EmailNotValidError, validate_email
from oes.auth.auth import AuthRepo, AuthService, Scope
from oes.auth.config import Config
from oes.auth.device import DeviceAuthOptions, DeviceAuthService
from oes.auth.email import EmailAuthService
from oes.auth.mq import MQService
from oes.auth.policy import is_allowed
from oes.auth.service import AccessTokenService, RefreshTokenService
from oes.auth.token import AccessToken, RefreshToken, RefreshTokenRepo, TokenError
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, Forbidden, HTTPResponse, Request, Unauthorized, json
from sanic.compat import Header
from sanic.exceptions import HTTPException, NotFound
from sanic.request import RequestParameters

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


@frozen
class CheckDeviceAuthRequest:
    """Check device auth request body."""

    user_code: str


@frozen
class AuthorizeDeviceRequest:
    """Authorize device request body."""

    user_code: str
    options: DeviceAuthOptions = DeviceAuthOptions()


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
        return HTTPResponse(
            status=204, headers=Header(("x-scope", s.value) for s in Scope)
        )

    # return 204 for options
    orig_method = request.headers.get("x-original-method", "")
    if orig_method == "OPTIONS":
        return HTTPResponse(status=204)

    orig_uri = request.headers.get("x-original-uri", "")

    token = _validate_token(request, access_token_service)

    response_headers = Header()

    if token.sub:
        response_headers["x-account-id"] = token.sub

    if token.email:
        response_headers["x-email"] = token.email

    if token.role:
        response_headers["x-role"] = token.role

    for scope in token.scope:
        response_headers.add("x-scope", scope)

    allowed = is_allowed(orig_method, orig_uri, token.scope)

    if not allowed:
        raise Forbidden

    return HTTPResponse(status=204, headers=response_headers)


@routes.get("/auth/cors")
async def cors(request: Request) -> HTTPResponse:
    """No-op endpoint to provide CORS headers."""
    return HTTPResponse(status=204)


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
    if config.disable_auth:
        scope = tuple(s.value for s in Scope)
        path_length = 3
    else:
        scope = (Scope.selfservice, Scope.cart)
        path_length = 0

    async with transaction():
        auth = auth_service.create_auth(scope=scope, path_length=path_length)
        refresh_token = await refresh_token_service.create(auth)
        access_token = refresh_token.make_access_token(now=refresh_token.date_created)
        return _make_token_response(access_token, refresh_token, config)


@routes.post("/auth/token")
async def token_endpoint(
    request: Request,
    refresh_token_service: RefreshTokenService,
    device_auth_service: DeviceAuthService,
    config: Config,
) -> HTTPResponse:
    """Token endpoint."""
    form = request.form
    if not form:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})

    grant_type = form.get("grant_type")
    response_type = form.get("response_type")
    refresh_token_str = form.get("refresh_token")

    if response_type == "device_code":
        return await _start_device_auth(device_auth_service)
    elif grant_type == "refresh_token":
        return await _refresh_token(refresh_token_str, refresh_token_service, config)
    elif grant_type == "device_code":
        return await _complete_device_auth(form, device_auth_service, config)
    else:
        raise Unauthorized(headers={"WWW-Authenticate": 'Bearer realm="OES"'})


async def _refresh_token(
    refresh_token_str: str | None,
    refresh_token_service: RefreshTokenService,
    config: Config,
) -> HTTPResponse:
    if not refresh_token_str:
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


@routes.post("/auth/device/check")
async def check_device_auth(
    request: Request,
    device_auth_service: DeviceAuthService,
    access_token_service: AccessTokenService,
    body: CattrsBody,
) -> HTTPResponse:
    """Check device auth user code."""
    token = _validate_token(request, access_token_service)
    req = await body(CheckDeviceAuthRequest)

    res = await device_auth_service.check_auth(token.sub, req.user_code)
    if res is not None:
        return json(
            {
                "roles": {
                    r: {"title": cfg.title, "scope": list(cfg.scope)}
                    for r, cfg in res.items()
                }
            }
        )
    else:
        raise NotFound


@routes.post("/auth/device/authorize")
async def authorize_device(
    request: Request,
    device_auth_service: DeviceAuthService,
    access_token_service: AccessTokenService,
    body: CattrsBody,
) -> HTTPResponse:
    """Authorize a device."""
    token = _validate_token(request, access_token_service)
    req = await body(AuthorizeDeviceRequest)

    async with transaction():
        res = await device_auth_service.authorize(req.user_code, token.sub, req.options)
    if res is None:
        raise NotFound
    elif res is False:
        raise Forbidden
    else:
        return HTTPResponse(status=204)


async def _start_device_auth(
    service: DeviceAuthService,
) -> HTTPResponse:
    """Start device auth."""
    async with transaction():
        auth = await service.create_auth()
    return json(
        {
            "user_code": auth.user_code,
            "device_code": auth.device_code,
        }
    )


async def _complete_device_auth(
    form: RequestParameters,
    service: DeviceAuthService,
    config: Config,
) -> HTTPResponse:
    """Complete device auth."""
    device_code = form.get("code") or ""

    async with transaction():
        res = await service.complete_auth(device_code)

    if res is None:
        return json({"error": "access_denied"}, status=400)
    elif res is False:
        return json({"error": "authorization_pending"}, status=400)
    else:
        access_token = res.make_access_token()
        return _make_token_response(access_token, res, config)


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
        "scope": " ".join(access_token.scope),
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
