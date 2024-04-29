"""Batch change routes."""

from collections.abc import Sequence

from attrs import define
from oes.registration.batch import BatchChangeService
from oes.registration.registration import Registration, RegistrationBatchChangeFields
from oes.registration.routes.common import response_converter
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, HTTPResponse, Request

routes = Blueprint("batch")


@define
class ChangeResultBody:
    """The result of a batch change."""

    passed: Sequence[Registration]
    failed: Sequence[Registration]


@routes.post("/check")
async def check_changes(
    request: Request,
    event_id: str,
    service: BatchChangeService,
    body: CattrsBody,
) -> HTTPResponse:
    """Test a batch of changes."""
    changes = await body(list[RegistrationBatchChangeFields])
    passed, failed = await service.check(event_id, changes)

    response = response_converter.make_response(ChangeResultBody(passed, failed))

    if failed:
        response.status = 409

    return response


@routes.post("/apply")
async def apply_changes(
    request: Request,
    event_id: str,
    service: BatchChangeService,
    body: CattrsBody,
) -> HTTPResponse:
    """Apply a batch of changes."""
    changes = await body(list[RegistrationBatchChangeFields])

    async with transaction():
        passed, failed = await service.check(event_id, changes, lock=True)

        if failed:
            response = response_converter.make_response(
                ChangeResultBody(passed, failed)
            )
            response.status = 409
            return response
        else:
            final = await service.apply(event_id, changes, passed)
            await transaction.commit()
            response = response_converter.make_response(ChangeResultBody(final, ()))
            return response
