"""Self service routes."""

from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlunparse

from attrs import frozen
from loguru import logger
from oes.utils.request import CattrsBody, raise_not_found
from oes.utils.template import TemplateContext
from oes.web.cart import CartService
from oes.web.config import Config, Event, InterviewOption, RegistrationDisplay
from oes.web.interview import InterviewService
from oes.web.registration import AddRegistrationError, RegistrationService, add_to_cart
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

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")
    access_code_str = request.args.get("access_code")
    access_code = (
        await service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )

    regs = await _get_regs(service, event_id, account_id, email, access_code)

    event_ctx = event.get_template_context()
    results = []

    for reg in regs:
        change_opts = list(service.get_change_options(event, reg, access_code))
        results.append(
            SelfServiceRegistration.from_registration(
                event.registration_display, event_ctx, change_opts, reg
            )
        )

    results.reverse()

    add_opts = [
        SelfServiceInterviewOption(opt.id, opt.title)
        for opt in service.get_add_options(event, access_code)
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

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")

    cart_id = request.args.get("cart_id")
    registration_id = request.args.get("registration_id")
    access_code = request.args.get("access_code")
    cart = await cart_service.get_cart(cart_id) if cart_id else None
    reg = (
        await reg_service.get_registration(event_id, registration_id)
        if registration_id
        else None
    )

    access_code_data = (
        await _check_access_code_use(access_code, event.id, cart, reg_service)
        if cart
        else None
    )

    if (
        not cart
        or cart.get("cart", {}).get("event_id") != event_id
        or registration_id
        and reg is None
        or not reg_service.is_interview_allowed(
            interview_id, event, reg, access_code_data
        )
    ):
        raise NotFound

    update_url = urlunparse(
        (request.scheme, request.host, "/update-interview", None, None, None)
    )
    target_url = request.url_for("selfservice.add_to_cart")

    access_code_interview = _get_access_code_interview(
        access_code_data, reg, interview_id
    )
    context, initial_data = _get_access_code_initial_data(
        access_code, access_code_interview
    )

    interview = await interview_service.start_interview(
        event,
        interview_id,
        cart_id,
        request.host,
        target_url,
        account_id,
        email,
        reg,
        context,
        initial_data,
    )
    return json({**interview, "update_url": update_url})


@routes.post("/self-service/add-to-cart", name="add_to_cart")
async def self_service_add_to_cart(
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

    target = completed_interview.target
    expected_target = request.url
    if target != expected_target:
        raise Forbidden

    try:
        result = await add_to_cart(
            completed_interview, registration_service, cart_service
        )
    except AddRegistrationError as e:
        logger.error(f"Cannot add to cart: {e}")
        raise Conflict from e

    return json({"id": result.get("id")})


async def _get_regs(
    service: RegistrationService,
    event_id: str,
    account_id: str | None,
    email: str | None,
    access_code: Mapping[str, Any] | None,
) -> Sequence[Mapping[str, Any]]:
    if access_code:
        opts = access_code.get("options", {})
        registration_ids = opts.get("registration_ids", [])
        if registration_ids:
            # could make a batch get method to improve this
            regs = [
                await service.get_registration(event_id, reg_id)
                for reg_id in registration_ids
            ]
            return [r for r in regs if r]

    return await service.get_registrations(
        event_id=event_id, account_id=account_id, email=email
    )


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


async def _check_access_code_use(
    access_code: str | None,
    event_id: str,
    cart: Mapping[str, Any],
    registration_service: RegistrationService,
) -> Mapping[str, Any] | None:
    if not access_code:
        return None

    cart_data = cart.get("cart", {})
    registrations = cart_data.get("registrations", [])
    for reg in registrations:
        meta = reg.get("meta", {})
        reg_access_code = meta.get("access_code")
        if access_code == reg_access_code:
            raise Conflict

    code = await registration_service.get_access_code(event_id, access_code)
    if code is None:
        raise Conflict
    return code


def _get_access_code_initial_data(
    access_code: str | None,
    interview_options: Mapping[str, Any] | None,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    context = interview_options.get("context", {}) if interview_options else {}
    if access_code:
        context["access_code"] = access_code
    initial_data = (
        interview_options.get("initial_data", {}) if interview_options else {}
    )
    return context, initial_data


def _get_access_code_interview(
    access_code_data: Mapping[str, Any] | None,
    reg: Mapping[str, Any] | None,
    interview_id: str,
) -> Mapping[str, Any] | None:
    options = access_code_data.get("options", {}) if access_code_data else {}
    interview_options = options.get(
        "add_options" if reg is None else "change_options", []
    )
    by_id = next(
        (opt for opt in interview_options if opt.get("id") == interview_id), None
    )
    return by_id
