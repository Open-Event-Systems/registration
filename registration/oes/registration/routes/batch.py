"""Batch change routes."""

from collections.abc import Mapping, Sequence
from typing import Any

from attrs import define, field
from oes.registration.batch import BatchChangeResult, BatchChangeService
from oes.registration.mq import MQService
from oes.registration.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationChangeResult,
)
from oes.registration.routes.common import response_converter
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody
from sanic import Blueprint, HTTPResponse, NotFound, Request, json
from sqlalchemy.exc import IntegrityError

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
    access_codes: Mapping[str, str] = field(factory=dict)
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
    req_body = await body(BatchChangeRequestBody)
    _, _, results = await service.check(
        event_id, req_body.changes, req_body.access_codes
    )

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
    message_queue: MQService,
) -> HTTPResponse:
    """Apply a batch of changes."""
    req_body = await body(BatchChangeRequestBody)

    async with transaction():
        current, access_codes, results = await service.check(
            event_id, req_body.changes, req_body.access_codes, lock=True
        )
        old_data = {
            cur.id: response_converter.converter.unstructure(cur)
            for cur in current.values()
        }

        if any(r.errors for r in results):
            response = response_converter.make_response(CheckResultBody(results))
            response.status = 409
            return response
        else:
            try:
                final = await service.apply(
                    event_id, req_body.changes, access_codes, current
                )
            except IntegrityError:
                await transaction.rollback()
                return json(None, status=409)
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

            for reg in final:
                await message_queue.publish_registration_update(
                    RegistrationChangeResult(reg.id, old_data.get(reg.id, {}), reg)
                )

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
