"""Registration routes."""

from collections.abc import Sequence
from datetime import datetime

from oes.registration.event import EventStatsService
from oes.registration.mq import MQService
from oes.registration.registration import (
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
from sanic import Blueprint, HTTPResponse, Request, SanicException

routes = Blueprint("registrations")


@routes.get("/")
@response_converter
async def list_registrations(
    request: Request,
    event_id: str,
    registration_repo: RegistrationRepo,
) -> Sequence[Registration]:
    """List registrations."""
    q = request.args.get("q", "")
    all = request.args.get("all") == "true"
    before_date_str = request.args.get("before_date")
    before_id = request.args.get("before_id")
    before_date = _parse_date(before_date_str) if before_date_str else None
    account_id = request.args.get("account_id")
    email = request.args.get("email")

    if before_date and before_id:
        before = (before_date, before_id)
    else:
        before = None
    return await registration_repo.search(
        event_id=event_id,
        query=q.lower().strip(),
        all=all,
        account_id=account_id,
        email=email,
        before=before,
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
    reg_create = await body(RegistrationCreateFields)
    async with transaction():
        res = await reg_service.create(event_id, reg_create)

    await message_queue.publish_registration_update(res)

    return response_converter.make_response(res.registration)


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
    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.get("/by-check-in/<check_in_id>")
@response_converter
async def read_registration_by_check_in_id(
    request: Request,
    event_id: str,
    check_in_id: str,
    registration_repo: RegistrationRepo,
) -> Registration:
    """Read a registration by check-in ID."""
    reg = raise_not_found(
        await registration_repo.get_by_check_in_id(event_id, check_in_id)
    )
    return reg


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
    etag = request.headers.get("ETag")
    update = await body(RegistrationUpdateFields)
    if update.version is None and etag is None:
        raise SanicException("Version or ETag required", status_code=428)

    async with transaction():
        res = raise_not_found(
            await reg_service.update(event_id, registration_id, update, etag=etag)
        )

    await message_queue.publish_registration_update(res)

    response = response_converter.make_response(res.registration)
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
            raise SanicException(str(e), status_code=409) from e

        if changed:
            await event_stats_service.assign_numbers(event_id, (reg,))

    if changed:
        change = RegistrationChangeResult(reg.id, old, reg)
        await message_queue.publish_registration_update(change)

    response = response_converter.make_response(reg)
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

    response = response_converter.make_response(reg)
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

    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response
