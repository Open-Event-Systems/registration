"""Registration routes."""

from collections.abc import Sequence
from uuid import UUID

from oes.registration.event import EventStatsService
from oes.registration.registration import (
    Registration,
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
    account_id = request.args.get("account_id")
    email = request.args.get("email")
    return await registration_repo.search(
        event_id=event_id, account_id=account_id, email=email
    )


@routes.post("/")
@response_converter
@transaction
async def create_registration(
    request: Request, event_id: str, reg_service: RegistrationService, body: CattrsBody
) -> Registration:
    """Create a registration."""
    reg_create = await body(RegistrationCreateFields)
    reg = await reg_service.create(event_id, reg_create)
    return reg


@routes.get("/<registration_id:uuid>")
async def read_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
) -> HTTPResponse:
    """Read a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>")
async def update_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    reg_service: RegistrationService,
    body: CattrsBody,
) -> HTTPResponse:
    """Update a registration."""
    etag = request.headers.get("ETag")
    update = await body(RegistrationUpdateFields)
    if update.version is None and etag is None:
        raise SanicException("Version or ETag required", status_code=428)

    async with transaction():
        reg = raise_not_found(
            await reg_service.update(event_id, registration_id, update, etag=etag)
        )

    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>/complete")
async def complete_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
    event_stats_service: EventStatsService,
) -> HTTPResponse:
    """Complete a registration."""
    async with transaction():
        reg = raise_not_found(
            await repo.get(registration_id, event_id=event_id, lock=True)
        )
        try:
            changed = reg.complete()
        except StatusError as e:
            raise SanicException(str(e), status_code=409) from e

        if changed:
            await event_stats_service.assign_numbers(event_id, (reg,))

    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>/cancel")
async def cancel_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
) -> HTTPResponse:
    """Cancel a registration."""
    async with transaction():
        reg = raise_not_found(
            await repo.get(registration_id, event_id=event_id, lock=True)
        )
        reg.cancel()

    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>/assign-number")
async def assign_number(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
    reg_service: RegistrationService,
    event_stats_service: EventStatsService,
) -> HTTPResponse:
    """Assign a number to a registration."""
    async with transaction():
        reg = raise_not_found(
            await repo.get(registration_id, event_id=event_id, lock=True)
        )

        await event_stats_service.assign_numbers(event_id, (reg,))

    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response
