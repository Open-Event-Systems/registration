"""Token endpoint."""
import asyncio

from blacksheep import Content, FromForm, Request, Response, allow_anonymous
from blacksheep.server.openapi.common import RequestBodyInfo, ResponseInfo
from oes.registration.app import app
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.credential_service import CredentialService
from oes.registration.auth.device_service import DeviceAuthService
from oes.registration.auth.oauth.server import CustomServer
from oes.registration.auth.scope import get_default_scopes
from oes.registration.config import CommandLineConfig
from oes.registration.database import transaction
from oes.registration.docs import docs
from oes.registration.models.config import Config


@allow_anonymous()
@app.router.post(
    "/auth/token",
)
@docs(
    request_body=RequestBodyInfo(
        examples={
            "refresh_token": {
                "client_id": "oes",
                "grant_type": "refresh_token",
                "refresh_token": "...",
            },
            "device_grant": {
                "client_id": "oes",
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": "...",
            },
        }
    ),
    responses={200: ResponseInfo("The token response")},
    tags=["OAuth"],
)
@transaction
async def token_endpoint(
    request: Request,
    form: FromForm,
    config: Config,
    cmd_config: CommandLineConfig,
    account_service: AccountService,
    credential_service: CredentialService,
    device_auth_service: DeviceAuthService,
) -> Response:
    """Token endpoint for OAuth."""
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
        server.create_token_response,
        str(request.url),
        "POST",
        form.value,
        headers,
    )

    response = Response(
        resp_status,
        [(k.encode(), v.encode()) for k, v in resp_headers.items()],
        Content(b"application/json", resp_body.encode()),
    )
    return response
