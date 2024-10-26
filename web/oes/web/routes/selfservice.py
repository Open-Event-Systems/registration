"""Self service routes."""

from collections.abc import Sequence

from attrs import frozen
from oes.utils.request import raise_not_found
from oes.utils.template import TemplateContext
from oes.web.access_code import AccessCodeService
from oes.web.cart import CartService
from oes.web.config import Config, Event, RegistrationDisplay
from oes.web.interview2 import InterviewService, InterviewState
from oes.web.registration2 import InterviewOption, RegistrationService
from oes.web.routes.common import response_converter
from oes.web.routes.event import EventResponse
from oes.web.selfservice import SelfServiceService, get_interview_data, options_include
from oes.web.types import Registration
from sanic import Blueprint, Forbidden, NotFound, Request
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
        registration: Registration,
    ) -> Self:
        """Create from a registration object."""
        ctx = {
            "event": event_ctx,
            "registration": dict(registration),
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
        (e for e in config.events.values() if e.visible),
        key=lambda e: e.date,
        reverse=True,
    )


@routes.get(
    "/self-service/events/<event_id>/registrations",
    name="list_selfservice_registrations",
)
@response_converter
async def list_selfservice_registrations(
    request: Request,
    event_id: str,
    access_code_service: AccessCodeService,
    self_service_service: SelfServiceService,
    config: Config,
) -> SelfServiceRegistrationsResponse:
    """List self-service registrations."""
    # TODO: should include cart ID
    event = raise_not_found(config.events.get(event_id))
    if not event.visible:
        raise NotFound

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")
    access_code_str = request.args.get("access_code")
    access_code = (
        await access_code_service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )
    access_code = access_code if access_code and access_code.valid else None

    event_ctx = event.get_template_context()

    registrations_opts = await self_service_service.get_registrations_and_options(
        event_id, account_id, email, access_code
    )

    results = []
    for reg, opts in registrations_opts:
        SelfServiceRegistration.from_registration(
            event.self_service.display, event_ctx, list(opts), reg
        )

    results.reverse()

    add_opts = [
        SelfServiceInterviewOption(opt.id, opt.title)
        for opt in self_service_service.get_add_options(event_id, access_code)
    ]

    return SelfServiceRegistrationsResponse(results, add_opts)


@routes.get("/self-service/events/<event_id>/interviews/<interview_id>")
@response_converter
async def start_interview(  # noqa: CCR001
    request: Request,
    event_id: str,
    interview_id: str,
    reg_service: RegistrationService,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    self_service_service: SelfServiceService,
    cart_service: CartService,
    config: Config,
) -> InterviewState:
    """Start an interview to add a registration to a cart."""
    event = raise_not_found(config.events.get(event_id))
    if not event.visible:
        raise NotFound
    elif not event.open:
        raise Forbidden

    account_id = request.headers.get("x-account-id")
    if not account_id:
        raise Forbidden
    email = request.headers.get("x-email")

    cart_id = request.args.get("cart_id")
    registration_id = request.args.get("registration_id")
    access_code_str = request.args.get("access_code")
    cart = await cart_service.get_cart(cart_id) if cart_id else None
    reg = (
        await reg_service.get_registration(event_id, registration_id)
        if registration_id
        else None
    )
    access_code = (
        await access_code_service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )
    access_code = access_code if access_code and access_code.valid else None

    if reg is not None:
        options = self_service_service.get_change_options(event_id, reg, access_code)
    else:
        options = self_service_service.get_add_options(event_id, access_code)

    if (
        not cart
        or cart.get("cart", {}).get("event_id") != event_id
        or registration_id
        and reg is None
        or access_code_str
        and access_code is None
        or not options_include(interview_id, options)
    ):
        raise NotFound

    target_url = request.url_for("carts.add_to_cart_from_interview", cart_id=cart_id)

    context, initial_data = get_interview_data(
        event, reg, interview_id, access_code, email, account_id
    )

    interview_state = await interview_service.start_interview(
        request.host, interview_id, target_url, context, initial_data
    )
    return interview_state
