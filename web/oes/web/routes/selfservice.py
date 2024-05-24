"""Self service routes."""

from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlunparse

from attrs import frozen
from oes.utils.request import CattrsBody, raise_not_found
from oes.utils.template import TemplateContext
from oes.web.cart import CartService
from oes.web.config import Config, Event, InterviewOption, RegistrationDisplay
from oes.web.interview import InterviewService
from oes.web.registration import RegistrationService
from oes.web.routes.common import Conflict, response_converter
from oes.web.routes.event import EventResponse
from sanic import Blueprint, Forbidden, HTTPResponse, NotFound, Request, json
from typing_extensions import Self

routes = Blueprint("selfservice")


@frozen
class SelfServiceInterviewOption:
    """Self service interview option."""

    id: str
    title: str | None = None


@frozen
class SelfServiceRegistration:
    """Self service registration."""

    id: str
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    header_color: str | None = None
    header_image: str | None = None
    change_options: Sequence[SelfServiceInterviewOption] = ()

    @classmethod
    def from_registration(
        cls,
        display: RegistrationDisplay,
        event_ctx: TemplateContext,
        change_opts: Sequence[InterviewOption],
        registration: Mapping[str, Any],
    ) -> Self:
        """Create from a registration object."""
        ctx = {
            "event": event_ctx,
            "registration": registration,
        }
        title = display.title.render(ctx)
        subtitle = display.subtitle.render(ctx) if display.subtitle else None
        description = display.description.render(ctx) if display.description else None
        header_color = (
            display.header_color.render(ctx) if display.header_color else None
        )
        header_image = (
            display.header_image.render(ctx) if display.header_image else None
        )
        return cls(
            registration["id"],
            title,
            subtitle,
            description,
            header_color,
            header_image,
            tuple(SelfServiceInterviewOption(opt.id, opt.title) for opt in change_opts),
        )


@frozen
class SelfServiceRegistrationsResponse:
    """Self service registrations listing."""

    registrations: Sequence[SelfServiceRegistration] = ()
    add_options: Sequence[SelfServiceInterviewOption] = ()


@frozen
class SelfServiceAddToCartRequest:
    """A request to add a registration to a cart."""

    state: str


@routes.get("/self-service/events")
@response_converter(list[EventResponse])
async def list_selfservice_events(request: Request, config: Config) -> list[Event]:
    """List self-service events."""
    return sorted(
        (e for e in config.events if e.visible), key=lambda e: e.date, reverse=True
    )


@routes.get(
    "/self-service/events/<event_id>/registrations",
    name="list_selfservice_registrations",
)
@response_converter
async def list_selfservice_registrations(
    request: Request, event_id: str, service: RegistrationService
) -> SelfServiceRegistrationsResponse:
    """List self-service registrations."""
    # TODO: should include cart ID
    event = raise_not_found(service.get_event(event_id))
    if not event.visible:
        raise NotFound

    regs = await service.get_registrations(event_id)

    event_ctx = event.get_template_context()
    results = []

    for reg in regs:
        change_opts = list(service.get_change_options(event, reg))
        results.append(
            SelfServiceRegistration.from_registration(
                event.registration_display, event_ctx, change_opts, reg
            )
        )

    add_opts = [
        SelfServiceInterviewOption(opt.id, opt.title)
        for opt in service.get_add_options(event)
    ]
    return SelfServiceRegistrationsResponse(results, add_opts)


@routes.get("/self-service/events/<event_id>/interviews/<interview_id>")
async def start_interview(
    request: Request,
    event_id: str,
    interview_id: str,
    reg_service: RegistrationService,
    interview_service: InterviewService,
    cart_service: CartService,
) -> HTTPResponse:
    """Start an interview to add a registration to a cart."""
    event = raise_not_found(reg_service.get_event(event_id))
    if not event.visible:
        raise NotFound
    elif not event.open:
        raise Forbidden

    cart_id = request.args.get("cart_id")
    registration_id = request.args.get("registration_id")
    cart = await cart_service.get_cart(cart_id) if cart_id else None
    reg = (
        await reg_service.get_registration(event_id, registration_id)
        if registration_id
        else None
    )
    if (
        not cart
        or cart.get("cart", {}).get("event_id") != event_id
        or registration_id
        and reg is None
        or not reg_service.is_interview_allowed(interview_id, event, reg)
    ):
        raise NotFound

    update_url = urlunparse(
        (request.scheme, request.host, "/update-interview", None, None, None)
    )
    target_url = request.url_for("selfservice.add_to_cart")

    interview = await interview_service.start_interview(
        event, interview_id, cart_id, target_url, reg
    )
    return json({**interview, "update_url": update_url})


@routes.post("/self-service/add-to-cart", name="add_to_cart")
async def add_to_cart(
    request: Request,
    body: CattrsBody,
    interview_service: InterviewService,
    cart_service: CartService,
    registration_service: RegistrationService,
) -> HTTPResponse:
    """Add a change to a cart via interview state."""
    req = await body(SelfServiceAddToCartRequest)
    state = req.state
    completed_interview = raise_not_found(
        await interview_service.get_completed_interview(state)
    )

    target = completed_interview.get("target")
    expected_target = request.url
    if target != expected_target:
        raise Forbidden

    data = completed_interview.get("data", {})
    context = completed_interview.get("context", {})
    cart_id = context.get("cart_id")
    interview_id = context.get("interview_id")
    event_id = context.get("event_id")
    registration = data.get("registration", {})

    event = raise_not_found(
        registration_service.get_event(event_id) if event_id else None
    )
    cur_exists, cur_reg = await _get_cur_registration(
        event.id, registration, registration_service
    )

    if (
        not cart_id
        or not interview_id
        or not event.visible
        or not event.open
        or not registration_service.is_interview_allowed(
            interview_id, event, cur_reg if cur_exists else None
        )
    ):
        raise Conflict

    if cur_reg.get("version") != registration.get("version"):
        raise Conflict

    new_cart = await cart_service.add_to_cart(
        cart_id,
        {
            "id": registration.get("id"),
            "old": cur_reg,
            "new": registration,
        },
    )
    return json({"id": new_cart.get("id")})


async def _get_cur_registration(
    event_id: str, reg: Mapping[str, Any], service: RegistrationService
) -> tuple[bool, Mapping[str, Any]]:
    reg_id = reg.get("id")
    cur = await service.get_registration(event_id, reg_id) if reg_id else None
    if cur:
        return True, cur
    else:
        return False, {
            "id": reg_id,
            "status": "pending",
            "version": 1,
        }
