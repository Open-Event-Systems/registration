"""Batch change routes."""

from collections.abc import Sequence

from attrs import define
from sanic import Blueprint, HTTPResponse, Request

from oes.registration_service.batch import BatchChangeService
from oes.registration_service.registration import (
    Registration,
    RegistrationBatchChangeFields,
)
from oes.registration_service.routes.common import response_converter
from oes.utils.request import CattrsBody

routes = Blueprint("batch")


@define
class ChangeResultBody:
    """The result of a batch change."""

    result: Sequence[Registration]
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
    current, failed = await service.check(event_id, changes)

    response = response_converter.make_response(ChangeResultBody(current, failed))

    if failed:
        response.status = 409

    return response
