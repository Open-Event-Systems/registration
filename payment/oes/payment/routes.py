"""Web routes."""

from collections.abc import Iterator, Mapping, Sequence
from datetime import datetime
from typing import Any

from attrs import frozen
from oes.payment.mq import MQService
from oes.payment.payment import (
    Payment,
    PaymentMethodError,
    PaymentNotFoundError,
    PaymentOption,
    PaymentServiceUnsupported,
    PaymentStatus,
)
from oes.payment.pricing import PricingResult
from oes.payment.service import PaymentRepo, PaymentServicesSvc, PaymentSvc
from oes.payment.types import CartData, PaymentInfoURLService, PaymentService
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody, raise_not_found
from oes.utils.response import ResponseConverter
from sanic import BadRequest, Blueprint, HTTPResponse, NotFound, Request
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
class PaymentSearchResult:
    """Payment search response body."""

    id: str
    service_name: str
    external_id: str
    cart_id: str
    cart_data: CartData
    receipt_id: str | None
    payment_url: str | None
    status: PaymentStatus
    date_created: datetime
    date_closed: datetime | None


@frozen
class PaymentResponse:
    """Payment response body."""

    id: str
    service: str
    external_id: str
    receipt_id: str | None
    status: PaymentStatus
    date_created: datetime
    date_closed: datetime | None
    cart_id: str
    cart_data: CartData
    pricing_result: Mapping[str, Any]
    data: Mapping[str, Any]


@frozen
class ReceiptResponse:
    """Receipt response body."""

    date_created: datetime
    date_closed: datetime | None
    pricing_result: Mapping[str, Any]


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
    role = request.headers.get("x-role")
    options = []
    for method_id, method_config in services_svc.get_methods(
        req.cart_data, req.pricing_result, role
    ):
        options.append(PaymentOption(id=method_id, name=method_config.name))

    return options


@routes.get("/payments")
@response_converter
async def list_payments(
    request: Request,
    payment_repo: PaymentRepo,
    payment_services_svc: PaymentServicesSvc,
) -> Sequence[PaymentSearchResult]:
    """List payments."""
    event_id = request.args.get("event_id")
    registration_id = request.args.get("registration_id")
    suspended = request.args.get("suspended")
    q = request.args.get("q")
    if not event_id or (not registration_id and not (suspended and q)):
        raise BadRequest

    if registration_id:
        res = await payment_repo.get_by_registration_id(event_id, registration_id)
    else:
        res = await payment_repo.get_suspended(event_id, q or "")
    svc_ids = {r.service for r in res}
    services = {s: payment_services_svc.get_service(s) for s in svc_ids}
    services = {s: v for s, v in services.items() if v}
    svc_names = {s: services[s].name for s in services}

    return [
        PaymentSearchResult(
            r.id,
            svc_names.get(r.service, r.service),
            r.external_id,
            r.cart_id,
            r.cart_data,
            r.receipt_id,
            _get_payment_url(r, services.get(r.service)),
            r.status,
            r.date_created,
            r.date_closed,
        )
        for r in res
    ]


def _get_payment_url(payment: Payment, service: PaymentService | None) -> str | None:
    if isinstance(service, PaymentInfoURLService):
        return service.get_payment_info_url(payment)
    else:
        return None


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
    email = request.headers.get("x-email")
    role = request.headers.get("x-role")

    req = await body(CreatePaymentRequestBody)
    methods = dict(services_svc.get_methods(req.cart_data, req.pricing_result, role))
    method_config = raise_not_found(methods.get(method_id))
    try:
        res = await payment_svc.create_payment(
            method_config.service,
            method_config,
            req.cart_id,
            req.cart_data,
            req.pricing_result,
            email,
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
        receipt_id=payment.receipt_id,
        status=payment.status,
        date_created=payment.date_created,
        date_closed=payment.date_closed,
        cart_id=payment.cart_id,
        cart_data=payment.cart_data,
        pricing_result=payment.pricing_result,
        data=payment.data,
    )


@routes.post("/payments/<payment_id>/update")
@response_converter
async def update_payment(
    request: Request,
    payment_id: str,
    repo: PaymentRepo,
    payment_svc: PaymentSvc,
    message_queue: MQService,
) -> PaymentResultResponse:
    """Update a payment."""
    body = request.json or {}
    async with transaction():
        payment = raise_not_found(await repo.get(payment_id, lock=True))
        try:
            res = await payment_svc.update_payment(payment, body)
        except PaymentNotFoundError:
            raise NotFound
        except PaymentServiceUnsupported:
            raise NotFound
        except PaymentMethodError as e:
            raise UnprocessableEntity(str(e))
    await _send_receipt(message_queue, payment)
    return PaymentResultResponse(
        id=res.id,
        service=res.service,
        status=res.status,
        body=res.body,
    )


async def _send_receipt(message_queue: MQService, payment: Payment):
    if _should_send_receipt(payment.pricing_result):
        email_set = set(_get_emails(payment.cart_data))
        for email in email_set:
            await message_queue.publish(
                "email.receipt",
                {
                    "to": email,
                    "pricing_result": payment.pricing_result,
                    "receipt_id": payment.receipt_id,
                },
            )


def _should_send_receipt(pricing_result: Mapping[str, Any]):
    """Send receipt if any item is not normally free."""
    for reg in pricing_result["registrations"]:
        for li in reg["line_items"]:
            if li["price"] > 0:
                return True
    return False


def _get_emails(cart_data: Mapping[str, Any]) -> Iterator[str]:
    for reg in cart_data["registrations"]:
        data = reg.get("new", {})
        email = data.get("email")
        if email:
            yield email


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


@routes.get("/receipts/<receipt_id>")
@response_converter
async def read_receipt(
    request: Request, receipt_id: str, repo: PaymentRepo
) -> ReceiptResponse:
    """Read a payment by receipt id."""
    payment = raise_not_found(await repo.get_by_receipt_id(receipt_id))
    return ReceiptResponse(
        date_created=payment.date_created,
        date_closed=payment.date_closed,
        pricing_result=payment.pricing_result,
    )


@routes.get("/_healthcheck")
async def healthcheck(
    request: Request,
    repo: PaymentRepo,
    message_queue: MQService,
) -> HTTPResponse:
    """Health check endpoint."""
    await repo.get("")
    if not message_queue.ready:
        return HTTPResponse(status=503)
    return HTTPResponse(status=204)
