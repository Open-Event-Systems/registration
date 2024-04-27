"""Registration routes."""

from collections.abc import Sequence
from uuid import UUID

from sanic import Blueprint, HTTPResponse, Request, SanicException

from oes.registration.registration import (
    Registration,
    RegistrationCreate,
    RegistrationRepo,
    RegistrationUpdate,
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
    reg_create = await body(RegistrationCreate)
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
) -> HTTPResponse:
    """Read a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    response = response_converter.make_response(reg)
    response.headers["ETag"] = _get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>")
async def update_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
    body: CattrsBody,
) -> HTTPResponse:
    """Update a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    _check_etag(request, reg)

    update = await body(RegistrationUpdate)
    update.apply(reg)
    await repo.session.flush()

    response = response_converter.make_response(reg)
    response.headers["ETag"] = _get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>/complete")
async def complete_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
) -> HTTPResponse:
    """Complete a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    try:
        reg.complete()
    except StatusError as e:
        raise SanicException(str(e), status_code=409) from e

    await repo.session.flush()

    response = response_converter.make_response(reg)
    response.headers["ETag"] = _get_etag(reg)
    return response


@routes.put("/<registration_id:uuid>/cancel")
async def cancel_registration(
    request: Request,
    event_id: str,
    registration_id: UUID,
    repo: RegistrationRepo,
) -> HTTPResponse:
    """Cancel a registration."""
    reg = raise_not_found(await repo.get(registration_id, event_id=event_id))
    reg.cancel()

    await repo.session.flush()

    response = response_converter.make_response(reg)
    response.headers["ETag"] = _get_etag(reg)
    return response


def _check_etag(request: Request, registration: Registration):
    cur_etag = _get_etag(registration)
    sent_etag = request.headers.get("If-Match")
    if not sent_etag:
        raise SanicException(status_code=428)
    if sent_etag != cur_etag:
        raise SanicException(status_code=412)


def _get_etag(registration: Registration) -> str:
    return f'W/"{registration.version}"'
