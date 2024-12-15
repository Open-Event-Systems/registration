"""Registration routes."""

from collections.abc import Sequence
from datetime import datetime

from attrs import frozen
from oes.registration.event import EventStatsService
from oes.registration.mq import MQService
from oes.registration.registration import (
    ConflictError,
    Registration,
    RegistrationChangeResult,
    RegistrationCreateFields,
    RegistrationRepo,
    RegistrationService,
    RegistrationUpdateFields,
    StatusError,
)
from oes.registration.routes.common import response_converter
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody, raise_not_found
from sanic import Blueprint, HTTPResponse, Request
from sanic.exceptions import HTTPException

routes = Blueprint("registrations")


@frozen
class RegistrationResponse:
    """Registration response."""

    registration: Registration


@frozen
class RegistrationListResponse:
    """Registration list response."""

    registrations: Sequence[RegistrationResponse]


@frozen
class RegistrationCreateRequestBody:
    """Request body to create a registration."""

    registration: RegistrationCreateFields


@frozen
class RegistrationUpdateRequestBody:
    """Request body to update a registration."""

    registration: RegistrationUpdateFields


class Conflict(HTTPException):
    """Conflict exception."""

    message = "Version mismatch"
    status_code = 409
    quiet = True


class PreconditionFailed(HTTPException):
    """Precondition failed exception."""

    message = "Version or If-Match required"
    status_code = 428
    quiet = True


@routes.get("/")
@response_converter
async def list_registrations(
    request: Request,
    event_id: str,
    registration_repo: RegistrationRepo,
) -> RegistrationListResponse:
    """List registrations."""
    args = request.get_args(keep_blank_values=True)
    q = args.get("q", "") or ""
    all = args.get("all") == "true"
    check_in_id = args.get("check_in_id")
    before_date_str = args.get("before_date")
    before_id = args.get("before_id")
    before_date = _parse_date(before_date_str) if before_date_str else None
    account_id = args.get("account_id")
    email = args.get("email")

    if before_date and before_id:
        before = (before_date, before_id)
    else:
        before = None
    res = await registration_repo.search(
        event_id=event_id,
        query=q.lower().strip(),
        all=all,
        check_in_id=check_in_id,
        account_id=account_id,
        email=email,
        before=before,
    )
    return RegistrationListResponse(
        registrations=tuple(RegistrationResponse(r) for r in res)
    )


def _parse_date(s: str) -> datetime | None:
    try:
        return datetime.fromisoformat(s).astimezone()
    except Exception:
        return None


@routes.post("/")
async def create_registration(
    request: Request,
    event_id: str,
    reg_service: RegistrationService,
    message_queue: MQService,
    body: CattrsBody,
) -> HTTPResponse:
    """Create a registration."""
    reg_create = await body(RegistrationCreateRequestBody)
    async with transaction():
        res = await reg_service.create(event_id, reg_create.registration)

    await message_queue.publish_registration_update(res)

    return response_converter.make_response(RegistrationResponse(res.registration))


@routes.get("/<registration_id>")
async def read_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
) -> HTTPResponse:
    """Read a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    response = response_converter.make_response(RegistrationResponse(reg))
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id>")
async def update_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    reg_service: RegistrationService,
    message_queue: MQService,
    body: CattrsBody,
) -> HTTPResponse:
    """Update a registration."""
    if_match = request.headers.get("If-Match")
    update = await body(RegistrationUpdateRequestBody)
    if update.registration.version is None and if_match is None:
        raise PreconditionFailed

    try:
        async with transaction():
            res = raise_not_found(
                await reg_service.update(
                    event_id, registration_id, update.registration, etag=if_match
                )
            )
    except ConflictError:
        raise Conflict

    await message_queue.publish_registration_update(res)

    response = response_converter.make_response(RegistrationResponse(res.registration))
    response.headers["ETag"] = reg_service.get_etag(res.registration)
    return response


@routes.put("/<registration_id>/complete")
async def complete_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
    message_queue: MQService,
    event_stats_service: EventStatsService,
) -> HTTPResponse:
    """Complete a registration."""
    async with transaction():
        reg = raise_not_found(
            await repo.get(registration_id, event_id=event_id, lock=True)
        )
        old = response_converter.converter.unstructure(reg)
        try:
            changed = reg.complete()
        except StatusError as e:
            raise Conflict(str(e)) from e

        if changed:
            await event_stats_service.assign_numbers(event_id, (reg,))

    if changed:
        change = RegistrationChangeResult(reg.id, old, reg)
        await message_queue.publish_registration_update(change)

    response = response_converter.make_response(RegistrationResponse(reg))
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id>/cancel")
async def cancel_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
    message_queue: MQService,
) -> HTTPResponse:
    """Cancel a registration."""
    async with transaction():
        reg = raise_not_found(
            await repo.get(registration_id, event_id=event_id, lock=True)
        )
        old = response_converter.converter.unstructure(reg)
        changed = reg.cancel()

    if changed:
        change = RegistrationChangeResult(reg.id, old, reg)
        await message_queue.publish_registration_update(change)

    response = response_converter.make_response(RegistrationResponse(reg))
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id>/assign-number")
async def assign_number(
    request: Request,
    event_id: str,
    registration_id: str,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
    event_stats_service: EventStatsService,
    message_queue: MQService,
) -> HTTPResponse:
    """Assign a number to a registration."""
    async with transaction():
        reg = raise_not_found(
            await repo.get(registration_id, event_id=event_id, lock=True)
        )
        old = response_converter.converter.unstructure(reg)

        await event_stats_service.assign_numbers(event_id, (reg,))

    if old.get("number") != reg.number:
        change = RegistrationChangeResult(reg.id, old, reg)
        await message_queue.publish_registration_update(change)

    response = response_converter.make_response(RegistrationResponse(reg))
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response
