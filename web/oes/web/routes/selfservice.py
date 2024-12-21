"""Self service routes."""

from collections.abc import Sequence

from attrs import frozen
from oes.utils.request import raise_not_found
from oes.utils.template import TemplateContext
from oes.web.access_code import AccessCodeService
from oes.web.cart import CartService
from oes.web.config import Config, Event, RegistrationDisplay
from oes.web.interview import InterviewService, InterviewState
from oes.web.registration import InterviewOption, Registration, RegistrationService
from oes.web.routes.common import response_converter
from oes.web.routes.event import EventResponse
from oes.web.selfservice import SelfServiceService, get_interview_data, get_option
from sanic import Blueprint, Forbidden, NotFound, Request
from typing_extensions import Self

routes = Blueprint("selfservice")


@frozen
class SelfServiceInterviewOption:
    """Self service interview option."""

    url: str
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
        request: Request,
        cart_id: str,
        display: RegistrationDisplay,
        event_ctx: TemplateContext,
        change_opts: Sequence[InterviewOption],
        registration: Registration,
        access_code: str | None,
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
            tuple(
                SelfServiceInterviewOption(
                    (
                        request.url_for(
                            "selfservice.start_direct_change_interview",
                            event_id=event_ctx["id"],
                            interview_id=opt.id,
                            registration_id=registration["id"],
                            **({"access_code": access_code} if access_code else {}),
                        )
                        if opt.direct
                        else request.url_for(
                            "selfservice.start_cart_change_interview",
                            cart_id=cart_id,
                            interview_id=opt.id,
                            registration_id=registration["id"],
                            **({"access_code": access_code} if access_code else {}),
                        )
                    ),
                    opt.title,
                )
                for opt in change_opts
            ),
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
    event = raise_not_found(config.events.get(event_id))
    if not event.visible:
        raise NotFound

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")
    cart_id = request.args.get("cart_id")
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
        results.append(
            SelfServiceRegistration.from_registration(
                request,
                cart_id,
                event.self_service.display,
                event_ctx,
                list(opts),
                reg,
                access_code_str,
            )
        )

    results.reverse()

    add_opts = [
        SelfServiceInterviewOption(
            (
                request.url_for(
                    "selfservice.start_direct_add_interview",
                    interview_id=opt.id,
                    event_id=event_id,
                    **({"access_code": access_code_str} if access_code_str else {}),
                )
                if opt.direct
                else request.url_for(
                    "selfservice.start_cart_add_interview",
                    interview_id=opt.id,
                    cart_id=cart_id,
                    **({"access_code": access_code_str} if access_code_str else {}),
                )
            ),
            opt.title,
        )
        for opt in self_service_service.get_add_options(event_id, access_code)
    ]

    return SelfServiceRegistrationsResponse(results, add_opts)


# Start interviews


@routes.get(
    "/carts/<cart_id>/self-service/add/<interview_id>", name="start_cart_add_interview"
)
@response_converter
async def start_cart_add_interview(
    request: Request,
    cart_id: str,
    interview_id: str,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    self_service_service: SelfServiceService,
    cart_service: CartService,
    config: Config,
) -> InterviewState:
    """Start an interview to add a registration to a cart."""
    cart = raise_not_found(await cart_service.get_cart(cart_id))
    event_id = cart["cart"]["event_id"]
    event = config.events.get(event_id)
    if not event or not event.visible or not event.open:
        raise Forbidden

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")

    access_code_str = request.args.get("access_code")
    access_code = (
        await access_code_service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )

    options = self_service_service.get_add_options(event_id, access_code)
    option = get_option(interview_id, options)

    if (
        # no matching option
        not option
        # no valid access code
        or access_code_str
        and (not access_code or not access_code.valid)
        # using a direct option
        or option.direct
    ):
        raise Forbidden

    target_url = request.url_for("carts.add_to_cart_from_interview", cart_id=cart_id)

    context, initial_data = get_interview_data(
        event, None, interview_id, access_code, email, account_id
    )

    proto = request.headers.get("X-Forwarded-Proto")

    interview_state = await interview_service.start_interview(
        request.host, proto, interview_id, target_url, context, initial_data
    )
    return interview_state


# TODO: sort out these URLs better
@routes.get(
    "/carts/<cart_id>/self-service/change/<registration_id>/<interview_id>",
    name="start_cart_change_interview",
)
@response_converter
async def start_cart_change_interview(
    request: Request,
    cart_id: str,
    registration_id: str,
    interview_id: str,
    reg_service: RegistrationService,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    self_service_service: SelfServiceService,
    cart_service: CartService,
    config: Config,
) -> InterviewState:
    """Start an interview to add a change to a cart."""
    cart = raise_not_found(await cart_service.get_cart(cart_id))
    event_id = cart["cart"]["event_id"]
    event = config.events.get(event_id)
    if not event or not event.visible or not event.open:
        raise Forbidden

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")
    registration = raise_not_found(
        await reg_service.get_registration(event_id, registration_id)
        if registration_id
        else None
    )

    access_code_str = request.args.get("access_code")
    access_code = (
        await access_code_service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )

    options = self_service_service.get_change_options(
        event_id, registration, access_code
    )
    option = get_option(interview_id, options)

    if (
        # no matching option
        not option
        # no reg permission
        or not (
            registration.has_permission(account_id, email)
            or access_code
            and len(access_code.options.registration_ids) > 0
            and registration.id in access_code.options.registration_ids
        )
        # no valid access code
        or access_code_str
        and (not access_code or not access_code.valid)
        # using a direct option
        or option.direct
    ):
        raise Forbidden

    target_url = request.url_for("carts.add_to_cart_from_interview", cart_id=cart_id)

    context, initial_data = get_interview_data(
        event, registration, interview_id, access_code, email, account_id
    )

    proto = request.headers.get("X-Forwarded-Proto")

    interview_state = await interview_service.start_interview(
        request.host, proto, interview_id, target_url, context, initial_data
    )
    return interview_state


@routes.get(
    "/events/<event_id>/self-service/add-registration/<interview_id>",
    name="start_direct_add_interview",
)
@response_converter
async def start_direct_add_interview(
    request: Request,
    event_id: str,
    interview_id: str,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    self_service_service: SelfServiceService,
    config: Config,
) -> InterviewState:
    """Start an interview to add a registration directly."""
    event = config.events.get(event_id)
    if not event or not event.visible or not event.open:
        raise Forbidden

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")

    access_code_str = request.args.get("access_code")
    access_code = (
        await access_code_service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )

    options = self_service_service.get_add_options(event_id, access_code)
    option = get_option(interview_id, options)

    if (
        # no matching option
        not option
        # no valid access code
        or access_code_str
        and (not access_code or not access_code.valid)
        # not using a direct option
        or not option.direct
    ):
        raise Forbidden

    target_url = request.url_for(
        "registrations.update_registrations_from_interview", event_id=event_id
    )

    context, initial_data = get_interview_data(
        event, None, interview_id, access_code, email, account_id
    )

    proto = request.headers.get("X-Forwarded-Proto")

    interview_state = await interview_service.start_interview(
        request.host, proto, interview_id, target_url, context, initial_data
    )
    return interview_state


@routes.get(
    "/events/<event_id>/registrations/<registration_id>"
    "/self-service/change/<interview_id>",
    name="start_direct_change_interview",
)
@response_converter
async def start_direct_change_interview(
    request: Request,
    event_id: str,
    registration_id: str,
    interview_id: str,
    reg_service: RegistrationService,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    self_service_service: SelfServiceService,
    config: Config,
) -> InterviewState:
    """Start an interview to change a registration directly."""
    event = config.events.get(event_id)
    if not event or not event.visible or not event.open:
        raise Forbidden

    account_id = request.headers.get("x-account-id")
    email = request.headers.get("x-email")
    registration = raise_not_found(
        await reg_service.get_registration(event_id, registration_id)
        if registration_id
        else None
    )

    access_code_str = request.args.get("access_code")
    access_code = (
        await access_code_service.get_access_code(event_id, access_code_str)
        if access_code_str
        else None
    )

    options = self_service_service.get_change_options(
        event_id, registration, access_code
    )
    option = get_option(interview_id, options)

    if (
        # no matching option
        not option
        # no reg permission
        or not (
            registration.has_permission(account_id, email)
            or access_code
            and len(access_code.options.registration_ids) > 0
            and registration.id in access_code.options.registration_ids
        )
        # no valid access code
        or access_code_str
        and (not access_code or not access_code.valid)
        # not using a direct option
        or not option.direct
    ):
        raise Forbidden

    target_url = request.url_for(
        "registrations.update_registrations_from_interview", event_id=event_id
    )

    context, initial_data = get_interview_data(
        event, registration, interview_id, access_code, email, account_id
    )

    proto = request.headers.get("X-Forwarded-Proto")

    interview_state = await interview_service.start_interview(
        request.host, proto, interview_id, target_url, context, initial_data
    )
    return interview_state
