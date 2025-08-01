"""Payment routes."""

from collections.abc import Mapping
from typing import Any

from oes.utils.request import raise_not_found
from oes.web.payment import PaymentService
from sanic import Blueprint, HTTPResponse, NotFound, Request, json

routes = Blueprint("payment")


@routes.get("/carts/<cart_id>/payment-methods")
async def list_payment_methods(
    request: Request, cart_id: str, payment_service: PaymentService
) -> HTTPResponse:
    """List payment options for a cart."""
    role = request.headers.get("x-role")
    res = raise_not_found(await payment_service.get_payment_options(cart_id, role))
    return json(res)


@routes.post("/carts/<cart_id>/create-payment")
async def create_payment(
    request: Request, cart_id: str, payment_service: PaymentService
) -> HTTPResponse:
    """Create a payment for a cart."""
    method = request.args.get("method")
    if not method:
        raise NotFound

    email = request.headers.get("x-email")
    role = request.headers.get("x-role")

    res_status, res_body = raise_not_found(
        await payment_service.create_payment(cart_id, method, email, role)
    )

    if res_status == 409:
        resp = json(_strip_cart_error(res_body), status=res_status)
    else:
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

    if res_status == 409:
        payment = await payment_service.get_payment(payment_id)
        if payment and payment["status"] == "completed":
            # hack: payment already completed, just return success silently
            resp = json(
                {
                    "id": payment["id"],
                    "service": payment["service"],
                    "status": payment["status"],
                    "prev_status": payment["status"],
                    "body": {},
                },
                200,
            )
        else:
            resp = json(_strip_cart_error(res_body), status=res_status)
    elif res_status == 200:
        payment = res_body.get("payment", {})
        resp = json(payment, status=res_status)
    else:
        resp = json(res_body, status=res_status)
    return resp


def _strip_cart_error(cart_error: Mapping[str, Any]) -> Mapping[str, Any]:
    """Remove detailed data from the cart conflict response."""
    stripped = {"results": []}
    for res in cart_error.get("results", []):
        stripped["results"].append(
            {
                "change": {"id": res.get("change", {}).get("id")},
                "errors": res.get("errors", []),
            }
        )

    return stripped
