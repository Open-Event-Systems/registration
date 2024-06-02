"""Batch change routes."""

from collections.abc import Mapping, Sequence
from typing import Any

from attrs import define
from oes.registration.batch import BatchChangeResult, BatchChangeService
from oes.registration.registration import Registration, RegistrationBatchChangeFields
from oes.registration.routes.common import response_converter
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, HTTPResponse, NotFound, Request, json

routes = Blueprint("batch")


@define
class CheckResultBody:
    """The result of a batch change check."""

    results: Sequence[BatchChangeResult]


@define
class ApplyResultBody:
    """The result of a completed batch change."""

    results: Sequence[Registration]
    payment: Mapping[str, Any] | None = None


@define
class BatchChangeRequestBody:
    """Batch change body."""

    changes: Sequence[RegistrationBatchChangeFields]
    payment_url: str | None = None
    payment_body: Mapping[str, Any] | None = None


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
    req_body = await body(BatchChangeRequestBody)

    async with transaction():
        current, results = await service.check(event_id, req_body.changes, lock=True)

        if any(r.errors for r in results):
            response = response_converter.make_response(CheckResultBody(results))
            response.status = 409
            return response
        else:
            final = await service.apply(event_id, req_body.changes, current)
            payment_success, payment_status_code, payment_res = (
                await _handle_payment(
                    req_body.payment_url, req_body.payment_body, service
                )
                if req_body.payment_url
                else (True, 200, None)
            )
            if not payment_success:
                return json(payment_res, status=payment_status_code)
            await transaction.commit()
            response = response_converter.make_response(
                ApplyResultBody(final, payment_res)
            )
            return response


async def _handle_payment(
    payment_url: str,
    payment_body: Mapping[str, Any] | None,
    service: BatchChangeService,
) -> tuple[bool, int, Mapping[str, Any]]:
    payment_req_status, payment_res = await service.complete_payment(
        payment_url, payment_body or {}
    )
    if payment_req_status == 404:
        raise NotFound
    if payment_req_status != 200:
        await transaction.rollback()
        return False, payment_req_status, payment_res

    payment_status = payment_res.get("status")
    if payment_status != "completed":
        await transaction.rollback()
        return False, payment_req_status, payment_res
    else:
        return True, payment_req_status, payment_res
