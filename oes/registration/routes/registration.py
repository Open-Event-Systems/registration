"""Registration routes."""

from collections.abc import Sequence
from uuid import UUID

from sanic import Blueprint, HTTPResponse, Request, SanicException

from oes.registration.registration import (
    Registration,
    RegistrationCreateFields,
    RegistrationRepo,
    RegistrationService,
    RegistrationUpdateFields,
    StatusError,
)
from oes.registration.routes.common import response_converter
from oes.utils.request import CattrsBody, raise_not_found

routes = Blueprint("registrations")


@routes.get("/")
@response_converter
async def list_registrations(
    request: Request,
    event_id: str,
    registration_repo: RegistrationRepo,
) -> Sequence[Registration]:
    """List registrations."""
    return await registration_repo.search(event_id)


@routes.post("/")
@response_converter
async def create_registration(
    request: Request, event_id: str, repo: RegistrationRepo, body: CattrsBody
) -> Registration:
    """Create a registration."""
    reg_create = await body(RegistrationCreateFields)
    reg = reg_create.create(event_id)
    repo.add(reg)
    await repo.session.flush()
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
) -> HTTPResponse:
    """Complete a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    try:
        reg.complete()
    except StatusError as e:
        raise SanicException(str(e), status_code=409) from e

    await repo.session.flush()

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
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    reg.cancel()

    await repo.session.flush()

    response = response_converter.make_response(reg)
    response.headers["ETag"] = reg_service.get_etag(reg)
    return response
