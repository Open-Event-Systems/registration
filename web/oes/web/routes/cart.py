"""Cart routes."""

import asyncio
from collections.abc import Iterable, Mapping

from oes.utils.request import CattrsBody, raise_not_found
from oes.web.cart import CartService, make_cart_registration
from oes.web.interview import (
    CompletedInterview,
    InterviewRegistration,
    InterviewService,
    get_interview_registrations,
)
from oes.web.registration import Registration, RegistrationService
from oes.web.routes.common import Conflict, InterviewStateRequestBody
from oes.web.types import JSON
from sanic import Blueprint, Forbidden, HTTPResponse, Request, json

routes = Blueprint("carts")


@routes.post("/carts/<cart_id>/add", name="add_to_cart_from_interview")
async def add_to_cart_from_interview(
    request: Request,
    body: CattrsBody,
    cart_id: str,
    registration_service: RegistrationService,
    cart_service: CartService,
    interview_service: InterviewService,
) -> HTTPResponse:
    """Add to a cart by interview."""
    req_body = await body(InterviewStateRequestBody)
    interview = raise_not_found(
        await interview_service.get_completed_interview(req_body.state)
    )
    if interview.target != request.url:
        raise Forbidden

    cart = raise_not_found(await cart_service.get_cart(cart_id))

    if not _check_access_code(cart, interview):
        raise Conflict("Access code has already been used")

    int_regs = get_interview_registrations(interview)
    cur_regs = await _get_registrations(
        registration_service,
        cart["cart"]["event_id"],
        (i.registration.id for i in int_regs),
    )
    _check_versions(int_regs, cur_regs)
    cart_regs = [
        make_cart_registration(cur_regs.get(r.registration.id), r.registration, r.meta)
        for r in int_regs
    ]
    res = await cart_service.add_to_cart(cart_id, cart_regs)
    return json({"id": res["id"]})


async def _get_registrations(
    registration_service: RegistrationService, event_id: str, ids: Iterable[str]
) -> Mapping[str, Registration]:
    tasks = [registration_service.get_registration(event_id, id) for id in ids]
    res = await asyncio.gather(*tasks)
    by_id = {r.id: r for r in res if r is not None}
    return by_id


def _check_access_code(cart: JSON, interview: CompletedInterview) -> bool:
    access_codes = set()
    for reg in cart["cart"]["registrations"]:
        code = reg.get("meta", {}).get("access_code")
        if code:
            access_codes.add(code)

    used_access_code = interview.data.get("meta", {}).get("access_code")
    return not (used_access_code and used_access_code in access_codes)


def _check_versions(
    registrations: Iterable[InterviewRegistration],
    cur_registrations: Mapping[str, Registration],
):
    for reg in registrations:
        cur = cur_registrations.get(reg.registration.id)
        if cur and cur.version != reg.registration.version:
            raise Conflict
