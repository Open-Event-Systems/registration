"""Cart views."""
import uuid
from typing import Any, Mapping, Optional, Union
from uuid import UUID

from attrs import frozen
from blacksheep import (
    Content,
    FromJSON,
    FromQuery,
    HTTPException,
    Request,
    Response,
    auth,
)
from blacksheep.exceptions import NotFound
from blacksheep.messages import get_absolute_url_to_path
from blacksheep.server.openapi.common import ContentInfo, RequestBodyInfo, ResponseInfo
from blacksheep.url import build_absolute_url
from cattrs import BaseValidationError
from loguru import logger
from oes.registration.access_code.models import AccessCodeSettings
from oes.registration.access_code.service import AccessCodeService
from oes.registration.app import app
from oes.registration.auth.handlers import (
    RequireAdmin,
    RequireCart,
    RequireSelfServiceOrKiosk,
)
from oes.registration.auth.user import User
from oes.registration.cart.entities import CartEntity
from oes.registration.cart.models import (
    CartData,
    CartError,
    CartRegistration,
    PricingResult,
)
from oes.registration.cart.service import CartService, price_cart
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper, serialize
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.interview.service import InterviewService
from oes.registration.models.config import Config
from oes.registration.models.event import Event, EventConfig, SimpleEventInfo
from oes.registration.models.registration import Registration, RegistrationState
from oes.registration.serialization import get_converter
from oes.registration.services.registration import (
    RegistrationService,
    get_allowed_add_interviews,
    get_allowed_change_interviews,
)
from oes.registration.util import check_not_found, get_now, merge_dict
from oes.registration.views.responses import BodyValidationError, PricingResultResponse
from oes.util.blacksheep import FromAttrs


@frozen
class AddRegistrationDirectRequest:
    """Request body to add a registration directly to a cart."""

    registration: dict[str, Any]
    meta: Optional[dict[str, Any]] = None


@frozen
class AddRegistrationFromInterviewRequest:
    """Add a registration from a completed interview."""

    state: str


AddRegistrationRequest = Union[
    AddRegistrationDirectRequest, AddRegistrationFromInterviewRequest
]


@auth(RequireAdmin)
@app.router.post("/carts")
@docs(tags=["Cart"], responses={303: ResponseInfo("Redirect to the created cart")})
@transaction
async def create_cart(
    request: Request,
    body: FromAttrs[CartData],
    service: CartService,
    event_config: EventConfig,
) -> Response:
    """Create a cart."""
    cart_data = body.value

    # Check that the event exists
    event = event_config.get_event(cart_data.event_id)
    if not event:
        raise BodyValidationError(
            ValueError(f"Event ID not found: {cart_data.event_id}")
        )

    # Check that the new data is valid for each registration
    for cr in cart_data.registrations:
        _validate_registration(cr.new_data)

    # Create the cart
    entity = CartEntity.create(cart_data)
    entity = await service.save_cart(entity)

    # Redirect to new cart URL
    url = get_absolute_url_to_path(request, f"/carts/{entity.id}")

    return Response(
        303,
        headers=[
            (b"Location", url.value),
        ],
    )


@auth(RequireCart)
@app.router.get("/carts/empty")
@docs(
    responses={
        303: ResponseInfo("Redirect to the cart"),
    },
    tags=["Cart"],
)
@transaction
async def read_empty_cart(
    event_id: FromQuery[str],
    request: Request,
    service: CartService,
    event_config: EventConfig,
    user: User,
) -> Response:
    """Get an empty cart."""
    event = check_not_found(event_config.get_event(event_id.value))
    if not event.is_visible_to(user):
        raise NotFound

    cart_entity = await service.get_empty_cart(event.id)
    cart_url = get_absolute_url_to_path(request, f"/carts/{cart_entity.id}")
    return Response(
        303,
        headers=[
            (b"Location", cart_url.value),
        ],
    )


@auth(RequireCart)
@app.router.get("/carts/{id}")
@docs(
    responses={200: ResponseInfo("The cart data", content=[ContentInfo(CartData)])},
    tags=["Cart"],
)
async def read_cart(id: str, service: CartService) -> Response:
    """Read a cart."""
    cart = check_not_found(await service.get_cart(id))

    model = cart.get_cart_data_model()
    data_bytes = get_converter().dumps(model)

    return Response(
        200,
        headers=[
            (b"ETag", f'"{cart.id}"'.encode()),
        ],
        content=Content(
            b"application/json",
            data_bytes,
        ),
    )


@auth(RequireCart)
@app.router.get("/carts/{id}/pricing-result")
@docs_helper(
    response_type=PricingResultResponse,
    response_summary="The pricing result",
    tags=["Cart"],
)
@transaction
async def read_cart_pricing_result(
    id: str,
    service: CartService,
    event_config: EventConfig,
    config: Config,
) -> PricingResultResponse:
    """Get the cart pricing result."""
    cart = check_not_found(await service.get_cart(id))
    model = cart.get_cart_data_model()

    # don't price an empty cart
    if len(model.registrations) == 0:
        return PricingResultResponse(
            receipt_url=None,
            date=None,
            registrations=(),
            total_price=0,
        )

    if cart.pricing_result is None:
        event = check_not_found(event_config.get_event(model.event_id))

        result = await price_cart(
            model,
            config.payment.currency,
            event,
            config.hooks,
        )

        # since the pricing result here is not final, no need to lock anything
        cart.set_pricing_result(result)
    else:
        result = get_converter().structure(cart.pricing_result, PricingResult)

    return PricingResultResponse.create(result)


@auth(RequireCart)
@app.router.post("/carts/{id}/registrations")
@docs(
    request_body=RequestBodyInfo(
        description="The registration info, or interview state",
        examples={
            "direct": {
                "registration": {
                    "id": "105e8d85-4f06-42b4-98c0-11c3cd0fe3c6",
                    "event_id": "example-event",
                    "state": "created",
                    "date_created": "2020-01-01T12:00:00+00:00",
                    "version": 1,
                    "option_ids": ["attendee"],
                },
                "meta": {
                    "is_minor": True,
                },
            },
            "interview": {
                "state": "ZXhhbXBsZQ==",
            },
        },
    ),
    responses={303: ResponseInfo("Redirect to the new cart")},
    tags=["Cart"],
)
@transaction
async def add_registration_to_cart(
    id: str,
    request: Request,
    service: CartService,
    reg_service: RegistrationService,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    event_config: EventConfig,
    body: FromJSON[dict[str, Any]],
    user: User,
) -> Response:
    """Add a registration to a cart."""
    add_obj = _parse_add_body(body.value)

    cart_entity = check_not_found(await service.get_cart(id))
    cart = cart_entity.get_cart_data_model()
    event = check_not_found(event_config.get_event(cart.event_id))
    if not event.is_open_to(user):
        raise HTTPException(409)

    if isinstance(add_obj, AddRegistrationDirectRequest):
        new_cart_entity = await _add_direct(cart, add_obj, service, reg_service)
    else:
        current_url = build_absolute_url(
            request.scheme.encode(),
            request.host.encode(),
            request.base_path.encode(),
            request.url.path,
        ).value.decode()

        new_cart_entity = await _add_from_interview(
            cart,
            event,
            add_obj.state,
            current_url,
            user,
            service,
            reg_service,
            interview_service,
            access_code_service,
        )

    cart_url = get_absolute_url_to_path(request, f"/carts/{new_cart_entity.id}")

    return Response(
        303,
        headers=[
            (b"Location", cart_url.value),
        ],
    )


@auth(RequireCart)
@app.router.delete("/carts/{id}/registrations/{registration_id}")
@docs(
    responses={
        303: ResponseInfo("Redirect to the new cart"),
    },
    tags=["Cart"],
)
@transaction
async def remove_registration_from_cart(
    id: str,
    registration_id: UUID,
    request: Request,
    service: CartService,
    events: EventConfig,
    user: User,
) -> Response:
    """Remove a registration from a cart."""
    entity = check_not_found(await service.get_cart(id))
    cart = entity.get_cart_data_model()

    event = events.get_event(cart.event_id)
    if not event or not event.is_open_to(user):
        raise HTTPException(409)

    updated = cart.remove_registration(registration_id)
    if updated == cart:
        raise NotFound

    new_entity = CartEntity.create(updated)
    new_entity = await service.save_cart(new_entity)

    cart_url = get_absolute_url_to_path(request, f"/carts/{new_entity.id}")

    return Response(
        303,
        headers=[
            (b"Location", cart_url.value),
        ],
    )


@auth(RequireSelfServiceOrKiosk)
@app.router.get("/carts/{id}/new-interview")
@docs(
    responses={
        200: ResponseInfo(
            "An interview state response",
        )
    },
    tags=["Cart"],
)
@serialize(dict[str, Any])
async def create_cart_add_interview_state(
    request: Request,
    id: str,
    interview_id: FromQuery[str],
    registration_id: FromQuery[Optional[UUID]],
    access_code: FromQuery[Optional[str]],
    event_config: EventConfig,
    service: CartService,
    registration_service: RegistrationService,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
    user: User,
) -> Mapping[str, Any]:
    """Get an interview state to add a registration to a cart."""
    entity = check_not_found(await service.get_cart(id))
    cart = entity.get_cart_data_model()

    event = check_not_found(event_config.get_event(cart.event_id))
    if not event.is_open_to(user):
        raise HTTPException(409)

    access_code_settings = await _get_access_code(
        access_code.value, event.id, access_code_service
    )

    if registration_id.value is not None:
        registration = await _get_registration_for_change(
            registration_id.value, registration_service, user, access_code_settings
        )
    else:
        registration = None

    valid_interview_id = _check_interview_availability(
        interview_id.value, event, registration, access_code_settings, user
    )
    if not valid_interview_id:
        raise NotFound

    # Build state
    context = _get_interview_context(event)
    initial_data = _get_interview_initial_data(
        event.id, registration, user, access_code.value, access_code_settings
    )
    submission_id = uuid.uuid4().hex

    target_url = get_absolute_url_to_path(request, f"/carts/{entity.id}/registrations")

    response = await interview_service.start_interview(
        valid_interview_id,
        target_url=target_url.value.decode(),
        submission_id=submission_id,
        context=context,
        initial_data=initial_data,
    )

    return response


def _validate_registration(data: dict[str, Any]) -> Registration:
    """Validate that a :class:`Registration` is valid."""
    try:
        return get_converter().structure(data, Registration)
    except BaseValidationError as e:
        raise BodyValidationError(e)


async def _get_registration_for_change(
    id: UUID,
    service: RegistrationService,
    user: User,
    access_code_settings: AccessCodeSettings,
) -> RegistrationEntity:
    reg = await service.get_registration(id, include_accounts=True)
    if not reg:
        raise NotFound

    # Check that the user account is associated with this registration
    if (
        (
            not access_code_settings
            or not access_code_settings.registration_id
            or access_code_settings.registration_id != id
        )
        and (not user.id or user.id not in [a.id for a in reg.accounts])
        and (not user.email or not reg.email or user.email.lower() != reg.email.lower())
        and not user.is_admin
    ):
        raise NotFound

    return reg


def _get_interview_context(event: Event) -> dict[str, Any]:
    event_data = SimpleEventInfo.create(event)
    return {
        "event": get_converter().unstructure(event_data),
    }


def _get_interview_initial_data(
    event_id: str,
    registration: Optional[RegistrationEntity],
    user: Optional[User],
    access_code: Optional[str],
    access_code_settings: Optional[AccessCodeSettings],
) -> dict[str, Any]:
    if registration:
        model = registration.get_model()
        registration_data = get_converter().unstructure(model)
        meta = {}
    else:
        model = Registration(
            id=uuid.uuid4(),
            state=RegistrationState.created,
            event_id=event_id,
            version=1,
            date_created=get_now(),
        )
        registration_data = get_converter().unstructure(model)

        meta = (
            {
                "account_id": str(user.id),
                "email": user.email,
            }
            if user and user.id
            else {}
        )

    if access_code is not None:
        meta["access_code"] = access_code

    data = {
        "registration": registration_data,
        "meta": meta,
    }

    if access_code_settings is not None:
        merge_dict(data, access_code_settings.initial_data)

    return data


async def _add_direct(
    cart: CartData,
    add: AddRegistrationDirectRequest,
    service: CartService,
    reg_service: RegistrationService,
):
    new_reg = _parse_registration_data(add.registration)

    # All registrations going thru carts end up in the created state
    new_reg.state = RegistrationState.created

    # Get existing data
    cur_reg_entity = await reg_service.get_registration(new_reg.id)

    return await _add_to_cart(
        cart, cur_reg_entity, new_reg, None, None, add.meta, service
    )


async def _add_from_interview(
    cart: CartData,
    event: Event,
    state: str,
    current_url: str,
    user: User,
    service: CartService,
    reg_service: RegistrationService,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
):
    interview_result = await interview_service.get_result(state, target_url=current_url)
    if not interview_result:
        logger.debug("Interview result is not valid")
        raise HTTPException(409)

    # Get existing data
    new_reg = _parse_registration_data(interview_result.data.get("registration", {}))

    # All registrations going thru carts end up in the created state
    new_reg.state = RegistrationState.created

    cur_reg_entity = await reg_service.get_registration(new_reg.id)

    meta = interview_result.data.get("meta", {})

    access_code = meta.get("access_code")
    access_code_settings = await _get_access_code(
        access_code,
        event.id,
        access_code_service,
    )

    if access_code is not None and access_code_settings is None:
        logger.debug("Access code is not valid")
        raise HTTPException(409)

    # make sure interview is still available
    if not _check_interview_availability(
        interview_result.interview["id"],
        event,
        cur_reg_entity,
        access_code_settings,
        user,
    ):
        logger.debug("Interview is not available")
        raise HTTPException(409)

    # Add to cart
    return await _add_to_cart(
        cart,
        cur_reg_entity,
        new_reg,
        interview_result.submission_id,
        access_code,
        meta,
        service,
    )


async def _get_access_code(
    code: Optional[str],
    event_id: str,
    service: AccessCodeService,
) -> Optional[AccessCodeSettings]:
    if code:
        entity = await service.get_access_code(code)
        if entity and entity.event_id == event_id and entity.check_valid():
            return entity.get_settings()
    return None


def _parse_add_body(body: dict[str, Any]) -> AddRegistrationRequest:
    try:
        obj = get_converter().structure(body, AddRegistrationRequest)
    except BaseValidationError as e:
        raise BodyValidationError(e) from e
    return obj


def _check_interview_availability(
    interview_id: str,
    event: Event,
    registration: Optional[RegistrationEntity],
    access_code_settings: Optional[AccessCodeSettings],
    user: User,
) -> Optional[str]:
    """Check if the interview is permitted."""
    if registration:
        allowed = get_allowed_change_interviews(
            event, registration, user, access_code_settings
        )
    else:
        allowed = get_allowed_add_interviews(event, user, access_code_settings)

    if interview_id not in [o.id for o in allowed]:
        return None
    return interview_id


def _parse_registration_data(data: dict[str, Any]) -> Registration:
    try:
        registration = get_converter().structure(data, Registration)
    except BaseValidationError as e:
        raise BodyValidationError(e)
    return registration


async def _add_to_cart(
    cart: CartData,
    old_reg: Optional[RegistrationEntity],
    new_reg: Registration,
    submission_id: Optional[str],
    access_code: Optional[str],
    meta: Optional[dict[str, Any]],
    service: CartService,
) -> CartEntity:
    cr = CartRegistration.create(
        old_reg,
        new_reg,
        submission_id=submission_id,
        access_code=access_code,
        meta=meta,
    )

    try:
        new_cart = cart.add_registration(cr)
    except CartError as e:
        raise HTTPException(409, str(e))

    entity = CartEntity.create(new_cart)
    return await service.save_cart(entity)
