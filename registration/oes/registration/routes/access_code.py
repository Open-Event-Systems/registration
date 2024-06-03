"""Access code routes."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from attrs import frozen
from oes.registration.access_code import (
    AccessCodeOptions,
    AccessCodeRepo,
    AccessCodeService,
)
from oes.registration.routes.common import response_converter
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, HTTPResponse, NotFound, Request

routes = Blueprint("access_code")


@frozen
class AccessCodeResponse:
    """Access code response object."""

    code: str
    date_created: datetime
    date_expires: datetime
    used: bool
    name: str
    options: Mapping[str, Any]


@frozen
class CreateAccessCodeRequest:
    """Create access code request object."""

    name: str
    date_expires: datetime
    options: AccessCodeOptions


@routes.get("/")
@response_converter
async def list_access_codes(
    request: Request, event_id: str, service: AccessCodeService
) -> Sequence[AccessCodeResponse]:
    """List access codes."""
    codes = await service.list(event_id)
    return [
        AccessCodeResponse(
            code=c.code,
            date_created=c.date_created,
            date_expires=c.date_expires,
            used=c.used,
            name=c.name,
            options=c.options,
        )
        for c in codes
    ]


@routes.post("/")
@response_converter
@transaction
async def create_access_code(
    request: Request, event_id: str, service: AccessCodeService, cattrs_body: CattrsBody
) -> AccessCodeResponse:
    """Create an access code."""
    body = await cattrs_body(CreateAccessCodeRequest)
    c = await service.create(event_id, body.date_expires, body.name, body.options)
    return AccessCodeResponse(
        code=c.code,
        date_created=c.date_created,
        date_expires=c.date_expires,
        used=c.used,
        name=c.name,
        options=c.options,
    )


@routes.get("/<code>")
@response_converter
async def read_access_code(
    request: Request, event_id: str, code: str, repo: AccessCodeRepo
) -> AccessCodeResponse:
    """Check an access code."""
    obj = await repo.get(code)
    now = datetime.now().astimezone()
    if obj is None or obj.event_id != event_id or obj.used or obj.date_expires <= now:
        raise NotFound
    return AccessCodeResponse(
        code=obj.code,
        date_created=obj.date_created,
        date_expires=obj.date_expires,
        used=obj.used,
        name=obj.name,
        options=obj.options,
    )


@routes.get("/<code>/check")
@transaction
async def check_access_code(
    request: Request, event_id: str, code: str, repo: AccessCodeRepo
) -> HTTPResponse:
    """Check an access code."""
    obj = await repo.get(code)
    now = datetime.now().astimezone()
    if obj is None or obj.event_id != event_id or obj.used or obj.date_expires <= now:
        raise NotFound
    return HTTPResponse(status=204)


@routes.delete("/<code>")
@transaction
async def delete_access_code(
    request: Request, event_id: str, code: str, repo: AccessCodeRepo
) -> HTTPResponse:
    """Delete an access code."""
    obj = await repo.get(code)
    if obj is None or obj.event_id != event_id:
        raise NotFound
    await repo.delete(obj)
    return HTTPResponse(status=204)
