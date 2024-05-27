"""Payment routes."""

from oes.utils.request import raise_not_found
from oes.web.payment import PaymentService
from sanic import Blueprint, HTTPResponse, NotFound, Request, json

routes = Blueprint("payment")


@routes.get("/carts/<cart_id>/payment-methods")
async def list_payment_methods(
    request: Request, cart_id: str, payment_service: PaymentService
) -> HTTPResponse:
    """List payment options for a cart."""
    res = raise_not_found(await payment_service.get_payment_options(cart_id))
    return json(res)


@routes.post("/carts/<cart_id>/create-payment")
async def create_payment(
    request: Request, cart_id: str, payment_service: PaymentService
) -> HTTPResponse:
    """Create a payment for a cart."""
    method = request.args.get("method")
    if not method:
        raise NotFound
    res_status, res_body = raise_not_found(
        await payment_service.create_payment(cart_id, method)
    )
    resp = json(res_body, status=res_status)
    return resp


@routes.post("/payments/<payment_id>/update")
async def update_payment(
    request: Request, payment_id: str, payment_service: PaymentService
) -> HTTPResponse:
    """Update a payment."""
    body = request.json
    res_status, res_body = raise_not_found(
        await payment_service.update_payment(payment_id, body)
    )
    return json(res_body, res_status)
