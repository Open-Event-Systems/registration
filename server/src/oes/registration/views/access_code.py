"""Access code views."""
from datetime import datetime
from typing import Optional

from attrs import frozen
from blacksheep import FromQuery, Response, auth
from blacksheep.exceptions import NotFound
from oes.registration.access_code.models import AccessCodeSettings
from oes.registration.access_code.service import AccessCodeService
from oes.registration.app import app
from oes.registration.auth.handlers import RequireAdmin, RequireCart
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper
from oes.registration.util import check_not_found
from oes.registration.views.parameters import AttrsBody
from oes.registration.views.responses import AccessCodeListResponse, AccessCodeResponse


@frozen
class CreateAccessCodeRequest:
    """Request body for creating an access code."""

    event_id: str
    date_expires: datetime
    name: Optional[str]
    data: AccessCodeSettings


@auth(RequireAdmin)
@app.router.get("/access-code")
@docs_helper(
    response_type=list[AccessCodeListResponse],
    response_summary="The access codes",
    tags=["Access Code"],
)
async def list_access_codes(
    service: AccessCodeService, event_id: Optional[str], page: int, per_page: int
) -> list[AccessCodeListResponse]:
    """List access codes."""
    # TODO: permissions
    results = await service.list_access_codes(
        event_id=event_id, page=page, per_page=per_page
    )

    return [
        AccessCodeListResponse(
            code=r.code,
            event_id=r.event_id,
            name=r.name,
            used=r.used,
        )
        for r in results
    ]


@auth(RequireCart)
@app.router.get("/access-code/{code}")
@docs(
    tags=["Access Code"],
)
async def check_access_code(
    event_id: FromQuery[str],
    code: str,
    service: AccessCodeService,
) -> Response:
    """Check if an access code is usable."""
    entity = await service.get_access_code(code)
    if not entity or entity.event_id != event_id.value or not entity.check_valid():
        raise NotFound
    else:
        return Response(204)


@auth(RequireAdmin)
@app.router.post("/access-code")
@docs_helper(
    response_type=AccessCodeResponse,
    response_summary="The created access code",
    tags=["Access Code"],
)
@transaction
async def create_access_code(
    service: AccessCodeService,
    body: AttrsBody[CreateAccessCodeRequest],
) -> AccessCodeResponse:
    """Create an access code."""
    create = body.value
    result = await service.create_access_code(
        event_id=create.event_id,
        name=create.name,
        expiration_date=create.date_expires,
        settings=create.data,
    )

    return AccessCodeResponse.create(result)


@auth(RequireAdmin)
@app.router.delete("/access-code/{code}")
@docs(tags=["Access Code"])
@transaction
async def delete_access_code(service: AccessCodeService, code: str) -> Response:
    """Delete an access code."""
    result = check_not_found(await service.get_access_code(code))
    await service.delete_access_code(result)
    return Response(204)
