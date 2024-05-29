"""Web routes."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from attrs import frozen
from oes.payment.payment import (
    PaymentError,
    PaymentOption,
    PaymentServiceUnsupported,
    PaymentStatus,
)
from oes.payment.pricing import PricingResult
from oes.payment.service import PaymentRepo, PaymentServicesSvc, PaymentSvc
from oes.payment.types import CartData
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody, raise_not_found
from oes.utils.response import ResponseConverter
from sanic import Blueprint, NotFound, Request
from sanic.exceptions import HTTPException

routes = Blueprint("payment")
response_converter = ResponseConverter()


class UnprocessableEntity(HTTPException):
    """HTTP 422 exception."""

    status_code = 422
    quiet = True


@frozen
class CreatePaymentRequestBody:
    """The body of a create payment request."""

    cart_id: str
    cart_data: CartData
    pricing_result: PricingResult


@frozen
class PaymentResponse:
    """Payment response body."""

    id: str
    service: str
    external_id: str
    status: PaymentStatus
    date_created: datetime
    date_closed: datetime | None
    cart_id: str
    cart_data: CartData
    pricing_result: Mapping[str, Any]
    data: Mapping[str, Any]


@frozen
class PaymentResultResponse:
    """Payment result response body."""

    id: str
    service: str
    status: PaymentStatus
    body: Mapping[str, Any]


@routes.post("/payment-methods")
@response_converter(Sequence[PaymentOption])
async def list_options(
    request: Request, services_svc: PaymentServicesSvc, body: CattrsBody
) -> Sequence[PaymentOption]:
    """List available payment options."""
    req = await body(CreatePaymentRequestBody)
    options = []
    for method_id, method_config in services_svc.get_methods(
        req.cart_data, req.pricing_result
    ):
        options.append(PaymentOption(id=method_id, name=method_config.name))

    return options


@routes.post("/payments")
@transaction
@response_converter
async def create_payment(
    request: Request,
    services_svc: PaymentServicesSvc,
    payment_svc: PaymentSvc,
    body: CattrsBody,
) -> PaymentResultResponse:
    """Create a payment."""
    method_id = request.args.get("method")
    if not method_id:
        raise NotFound
    req = await body(CreatePaymentRequestBody)
    methods = dict(services_svc.get_methods(req.cart_data, req.pricing_result))
    method_config = raise_not_found(methods.get(method_id))
    try:
        res = await payment_svc.create_payment(
            method_config.service,
            method_config,
            req.cart_id,
            req.cart_data,
            req.pricing_result,
        )
    except PaymentServiceUnsupported:
        raise NotFound
    return PaymentResultResponse(
        id=res.id,
        service=res.service,
        status=res.status,
        body=res.body,
    )


@routes.get("/payments/<payment_id>")
@response_converter
async def read_payment(
    request: Request, payment_id: str, repo: PaymentRepo
) -> PaymentResponse:
    """Read a payment."""
    payment = raise_not_found(await repo.get(payment_id))
    return PaymentResponse(
        id=payment.id,
        service=payment.service,
        external_id=payment.external_id,
        status=payment.status,
        date_created=payment.date_created,
        date_closed=payment.date_closed,
        cart_id=payment.cart_id,
        cart_data=payment.cart_data,
        pricing_result=payment.pricing_result,
        data=payment.data,
    )


@routes.post("/payments/<payment_id>/update")
@transaction
@response_converter
async def update_payment(
    request: Request, payment_id: str, repo: PaymentRepo, payment_svc: PaymentSvc
) -> PaymentResultResponse:
    """Update a payment."""
    body = request.json or {}
    payment = raise_not_found(await repo.get(payment_id, lock=True))
    try:
        res = await payment_svc.update_payment(payment, body)
    except PaymentServiceUnsupported:
        raise NotFound
    except PaymentError as e:
        raise UnprocessableEntity(str(e))
    return PaymentResultResponse(
        id=res.id,
        service=res.service,
        status=res.status,
        body=res.body,
    )


@routes.put("/payments/<payment_id>/cancel")
@transaction
@response_converter
async def cancel_payment(
    request: Request, payment_id: str, repo: PaymentRepo, payment_svc: PaymentSvc
) -> PaymentResultResponse:
    """Cancel a payment."""
    payment = raise_not_found(await repo.get(payment_id, lock=True))
    try:
        res = await payment_svc.cancel_payment(payment)
    except PaymentServiceUnsupported:
        raise NotFound
    return PaymentResultResponse(
        id=res.id,
        service=res.service,
        status=res.status,
        body=res.body,
    )
