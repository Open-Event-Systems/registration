"""Batch change routes."""

from collections.abc import Sequence

from attrs import define
from oes.registration.batch import BatchChangeResult, BatchChangeService
from oes.registration.registration import Registration, RegistrationBatchChangeFields
from oes.registration.routes.common import response_converter
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, HTTPResponse, Request

routes = Blueprint("batch")


@define
class CheckResultBody:
    """The result of a batch change check."""

    results: Sequence[BatchChangeResult]


@define
class ApplyResultBody:
    """The result of a completed batch change."""

    results: Sequence[Registration]


@routes.post("/check")
async def check_changes(
    request: Request,
    event_id: str,
    service: BatchChangeService,
    body: CattrsBody,
) -> HTTPResponse:
    """Test a batch of changes."""
    changes = await body(list[RegistrationBatchChangeFields])
    _, results = await service.check(event_id, changes)

    response = response_converter.make_response(CheckResultBody(results))

    if any(r.errors for r in results):
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
        current, results = await service.check(event_id, changes, lock=True)

        if any(r.errors for r in results):
            response = response_converter.make_response(CheckResultBody(results))
            response.status = 409
            return response
        else:
            final = await service.apply(event_id, changes, current)
            await transaction.commit()
            response = response_converter.make_response(ApplyResultBody(final))
            return response
