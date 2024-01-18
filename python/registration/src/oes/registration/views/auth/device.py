"""Device auth views."""
from __future__ import annotations

import asyncio
from typing import Optional

from attr import frozen
from blacksheep import Content, FromForm, Request, Response, allow_anonymous
from blacksheep.exceptions import Forbidden
from blacksheep.server.openapi.common import RequestBodyInfo, ResponseInfo
from oes.registration.app import app
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.credential_service import CredentialService
from oes.registration.auth.device_service import (
    DeviceAuthService,
    authorize_device_auth,
)
from oes.registration.auth.oauth.server import CustomServer
from oes.registration.auth.scope import Scopes, get_default_scopes
from oes.registration.auth.user import User
from oes.registration.config import CommandLineConfig
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper
from oes.registration.models.config import Config
from oes.util.blacksheep import FromAttrs


@frozen
class CheckDeviceAuthRequest:
    """Check a user code."""

    user_code: str


@frozen
class AuthorizeDeviceAuthRequest:
    """Request to authorize a device."""

    user_code: str
    scope: Optional[str] = None
    new_account: bool = False
    email: Optional[str] = None
    require_webauthn: bool = False


@allow_anonymous()
@app.router.post(
    "/auth/authorize-device",
)
@docs(
    request_body=RequestBodyInfo(
        examples={"device_grant": {"client_id": "oes", "scope": "cart self-service"}}
    ),
    responses={200: ResponseInfo("The token response")},
    tags=["OAuth"],
)
@transaction
async def device_auth_endpoint(
    form: FromForm,
    request: Request,
    config: Config,
    cmd_config: CommandLineConfig,
    account_service: AccountService,
    device_auth_service: DeviceAuthService,
    credential_service: CredentialService,
) -> Response:
    """Device authorization endpoint."""
    loop = asyncio.get_running_loop()
    server = CustomServer(
        config.auth,
        get_default_scopes(cmd_config),
        account_service,
        credential_service,
        device_auth_service,
        loop,
    )

    headers = {k.decode(): v.decode() for k, v in request.headers.items()}

    resp_headers, resp_body, resp_status = await asyncio.to_thread(
        server.create_device_authorization_response,
        str(request.url),
        request.method,
        form.value,
        headers,
    )

    response = Response(
        resp_status,
        [(k.encode(), v.encode()) for k, v in resp_headers.items()],
        Content(b"application/json", resp_body.encode()),
    )
    return response


@frozen
class CheckDeviceAuthResponse:
    """Status of a device auth."""

    client: str
    scope: str


@app.router.post(
    "/auth/check-authorize-device",
)
@docs_helper(
    response_type=CheckDeviceAuthResponse,
    response_summary="The device auth information",
    tags=["OAuth"],
)
async def check_device_auth_endpoint(
    body: FromAttrs[CheckDeviceAuthRequest],
    device_auth_service: DeviceAuthService,
) -> CheckDeviceAuthResponse:
    """Check the status of a device authorization."""
    auth = await device_auth_service.get_by_user_code(body.value.user_code)
    if not auth or auth.account_id is not None or not auth.is_valid():
        raise Forbidden

    # TODO: keep these in an official place
    client_id_names = {"oes": "Registration", "oes.kiosk": "Registration Kiosk"}

    return CheckDeviceAuthResponse(
        client=client_id_names.get(auth.client_id, auth.client_id),
        scope=auth.scope,
    )


@app.router.post(
    "/auth/complete-authorize-device",
)
@docs(
    responses={200: ResponseInfo("The token response")},
    tags=["OAuth"],
)
@transaction
async def complete_device_auth_endpoint(
    body: FromAttrs[AuthorizeDeviceAuthRequest],
    device_auth_service: DeviceAuthService,
    account_service: AccountService,
    user: User,
) -> Response:
    """Complete device authorization."""
    auth = await device_auth_service.get_by_user_code(body.value.user_code)
    if not auth or not auth.is_valid():
        raise Forbidden

    if not await authorize_device_auth(
        auth,
        user,
        account_service,
        body.value.new_account,
        body.value.email,
        Scopes(body.value.scope) if body.value.scope is not None else user.scope,
        body.value.require_webauthn,
    ):
        raise Forbidden

    return Response(204)
