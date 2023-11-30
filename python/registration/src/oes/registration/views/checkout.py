"""Checkout views."""
from collections.abc import Iterable, Mapping
from typing import Optional
from uuid import UUID

from attrs import evolve
from blacksheep import (
    Content,
    FromBytes,
    FromJSON,
    FromQuery,
    HTTPException,
    Response,
    allow_anonymous,
    auth,
)
from blacksheep.exceptions import NotFound
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo
from loguru import logger
from oes.registration.access_code.entities import AccessCodeEntity
from oes.registration.access_code.service import AccessCodeService
from oes.registration.app import app
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.handlers import RequireCart, RequireCheckout
from oes.registration.auth.user import User
from oes.registration.cart.models import CartData, PricingResult
from oes.registration.cart.service import (
    CartService,
    get_access_codes_from_cart,
    get_registration_entities_from_cart,
    price_cart,
    validate_changes,
)
from oes.registration.checkout.entities import CheckoutEntity, CheckoutState
from oes.registration.checkout.models import PaymentServiceCheckout
from oes.registration.checkout.service import CheckoutService, apply_checkout_changes
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper
from oes.registration.entities.event_stats import EventStatsEntity
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.hook.service import HookSender
from oes.registration.models.config import Config
from oes.registration.models.event import EventConfig
from oes.registration.payment.base import CheckoutMethod
from oes.registration.payment.errors import CheckoutStateError, ValidationError
from oes.registration.serialization import get_converter
from oes.registration.serialization.common import structure_datetime
from oes.registration.services.event import EventService
from oes.registration.services.registration import (
    RegistrationService,
    assign_registration_numbers,
)
from oes.registration.util import check_not_found
from oes.registration.views.responses import (
    BodyValidationError,
    CheckoutErrorResponse,
    CheckoutListResponse,
    CheckoutResponse,
    PricingResultResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession


@auth(RequireCheckout)
@app.router.get("/checkouts")
@docs_helper(
    response_type=list[CheckoutListResponse],
    response_summary="The list of checkouts",
    tags=["Checkout"],
)
async def list_checkouts(
    checkout_service: CheckoutService,
    registration_id: Optional[UUID] = None,
    before: Optional[str] = None,
) -> list[CheckoutListResponse]:
    """List checkouts."""
    try:
        before_date = structure_datetime(before) if before else None
    except Exception:
        before_date = None

    entities = await checkout_service.list_checkouts(
        registration_id=registration_id, before=before_date
    )

    results = []
    for e in entities:
        try:
            service = checkout_service.get_payment_service(e.service)
            service_name = service.name
            url = service.get_url(e.external_id, e.external_data)
        except LookupError:
            service_name = e.service
            url = None

        results.append(
            CheckoutListResponse(
                id=e.external_id,
                state=e.state,
                date=e.date_closed if e.date_closed is not None else e.date_created,
                service=service_name,
                url=url,
            )
        )

    return results


@auth(RequireCart)
@app.router.get("/carts/{cart_id}/checkout-methods")
@docs_helper(
    response_type=list[CheckoutMethod],
    response_summary="The available checkout methods",
    tags=["Checkout"],
)
async def list_available_checkout_methods(
    cart_id: str,
    cart_service: CartService,
    checkout_service: CheckoutService,
    event_config: EventConfig,
    config: Config,
    user: User,
) -> list[CheckoutMethod]:
    """List checkout methods."""
    cart_entity = check_not_found(await cart_service.get_cart(cart_id))
    cart_data = cart_entity.get_cart_data_model()

    event = check_not_found(event_config.get_event(cart_data.event_id))
    if not event.is_open_to(user):
        raise HTTPException(409)

    # Price cart if unpriced, and ignore empty carts

    if len(cart_data.registrations) == 0:
        return []

    if cart_entity.pricing_result:
        pricing_result = get_converter().structure(
            cart_entity.pricing_result, PricingResult
        )
    else:
        pricing_result = await price_cart(
            cart_data, config.payment.currency, event, config.hooks
        )
        cart_entity.set_pricing_result(pricing_result)

    methods = await checkout_service.get_checkout_methods_for_cart(
        cart_data, pricing_result
    )

    return methods


@auth(RequireCart)
@app.router.post("/carts/{cart_id}/checkout")
@docs(
    responses={
        200: ResponseInfo(
            "The created checkout details",
            content=[ContentInfo(CheckoutResponse)],
        ),
        409: ResponseInfo(
            "Info about registrations that are out-of-date",
            content=[ContentInfo(CheckoutErrorResponse)],
        ),
    },
    tags=["Checkout"],
)
async def create_checkout(
    cart_id: str,
    service: FromQuery[str],
    method: FromQuery[str],
    cart_service: CartService,
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
    access_code_service: AccessCodeService,
    event_config: EventConfig,
    config: Config,
    db: AsyncSession,
    user: User,
    _body: Optional[FromBytes],
) -> Response:
    """Create a checkout for a cart."""
    cart_entity = check_not_found(await cart_service.get_cart(cart_id))
    cart = cart_entity.get_cart_data_model()

    if not checkout_service.is_service_available(service.value):
        raise NotFound

    event = check_not_found(event_config.get_event(cart.event_id))
    if not event.is_open_to(user):
        raise HTTPException(409)

    # make sure the changes can still be applied
    _, _, error_response = await _validate_changes(
        cart,
        registration_service,
        access_code_service,
        False,
    )

    if error_response:
        await db.rollback()
        return error_response

    # set user's email in cart metadata
    cart = evolve(cart, meta={"email": user.email, **(cart.meta or {})})

    # Price the cart (this will be the official price)
    pricing_result = await price_cart(
        cart, config.payment.currency, event, config.hooks
    )
    cart_entity.set_pricing_result(pricing_result)

    if not await _validate_checkout_method(
        service.value, method.value, cart, pricing_result, checkout_service
    ):
        await db.commit()
        raise NotFound

    checkout_entity, checkout = await checkout_service.create_checkout(
        service_id=service.value,
        cart_id=cart_id,
        cart_data=cart,
        pricing_result=pricing_result,
    )

    response = Response(
        200,
        content=Content(
            b"application/json",
            get_converter().dumps(
                CheckoutResponse(
                    id=checkout_entity.id,
                    service=checkout.service,
                    external_id=checkout.id,
                    state=checkout.state,
                    data=checkout.response_data,
                )
            ),
        ),
    )

    await db.commit()
    return response


@auth(RequireCart)
@app.router.put("/checkouts/{id}/cancel")
@docs(
    tags=["Checkout"],
)
@transaction
async def cancel_checkout(id: UUID, checkout_service: CheckoutService) -> Response:
    """Cancel a checkout."""
    # don't check event, permit checkout cancel even if event is missing/closed
    result = await checkout_service.cancel_checkout(id)
    if result is None:
        raise NotFound
    elif result is True:
        return Response(204)
    else:
        raise HTTPException(409, "Checkout could not be canceled")


@allow_anonymous()
@app.router.post("/checkouts/{id}/update")
@docs(
    responses={
        200: ResponseInfo(
            "An updated checkout", content=[ContentInfo(CheckoutResponse)]
        ),
        204: ResponseInfo("Returned when the checkout was completed"),
        422: ResponseInfo("An error with payment occurred"),
    },
    tags=["Checkout"],
)
async def update_checkout(
    id: UUID,
    body: FromJSON[dict],
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
    access_code_service: AccessCodeService,
    account_service: AccountService,
    event_service: EventService,
    events: EventConfig,
    hook_sender: HookSender,
    db: AsyncSession,
    user: Optional[User] = None,
) -> Response:
    """Update a checkout."""
    checkout = check_not_found(await checkout_service.get_checkout(id, lock=True))

    payment_service = checkout.service
    external_id = checkout.external_id

    cart_data = checkout.get_cart_data()

    _validate_checkout_and_event(checkout, cart_data, events, user)

    # lock rows and verify changes can be applied before completing the checkout
    if not checkout.changes_applied:
        registration_entities, access_codes, error_response = await _validate_changes(
            cart_data, registration_service, access_code_service, True
        )

        if error_response:
            await db.rollback()
            return error_response

    else:
        registration_entities = {}
        access_codes = {}

    result = await _update_checkout(body.value, checkout, checkout_service)

    # After this point, any error will roll back the database but will not cancel or
    # refund the transaction
    try:
        if result.state == CheckoutState.complete and not checkout.changes_applied:
            event_stats = await event_service.get_event_stats(
                cart_data.event_id, lock=True
            )

            await _apply_changes(
                checkout,
                registration_entities,
                access_codes,
                event_stats,
                registration_service,
                account_service,
                hook_sender,
            )

        await db.commit()
        return _make_checkout_update_response(result, checkout)
    except Exception:
        # TODO: use a specific logger?
        logger.opt(exception=True).error(
            f"{payment_service!r} checkout {external_id} failed to save changes "
            f"after updating the checkout. This may need to be resolved manually."
        )
        raise


def _validate_checkout_and_event(
    checkout: CheckoutEntity,
    cart_data: CartData,
    events: EventConfig,
    user: Optional[User],
):
    if not checkout.is_open:
        raise NotFound

    event = events.get_event(cart_data.event_id)
    if not event or not event.is_open_to(user):
        raise HTTPException(409)


async def _validate_changes(
    cart_data: CartData,
    registration_service: RegistrationService,
    access_code_service: AccessCodeService,
    lock: bool,
) -> tuple[
    Mapping[UUID, RegistrationEntity],
    Mapping[str, AccessCodeEntity],
    Optional[Response],
]:
    registrations = await get_registration_entities_from_cart(
        cart_data,
        registration_service,
        lock=lock,
    )

    access_codes = await get_access_codes_from_cart(
        cart_data, access_code_service, lock=lock
    )

    errors = validate_changes(cart_data, registrations, access_codes)

    if len(errors) > 0:
        return (
            registrations,
            access_codes,
            Response(
                409,
                content=Content(
                    b"application/json",
                    get_converter().dumps(
                        CheckoutErrorResponse(
                            errors={str(id_): err for id_, err in errors.items()}
                        )
                    ),
                ),
            ),
        )
    else:
        return registrations, access_codes, None


async def _update_checkout(
    body: dict,
    checkout: CheckoutEntity,
    checkout_service: CheckoutService,
) -> PaymentServiceCheckout:
    try:
        return await checkout_service.update_checkout(checkout, body)
    except ValidationError as e:
        raise BodyValidationError(e)
    except CheckoutStateError as e:
        raise HTTPException(409, str(e))


async def _apply_changes(
    checkout_entity: CheckoutEntity,
    registration_entities: Mapping[UUID, RegistrationEntity],
    access_codes: Mapping[str, AccessCodeEntity],
    event_stats: EventStatsEntity,
    registration_service: RegistrationService,
    account_service: AccountService,
    hook_sender: HookSender,
) -> list[RegistrationEntity]:
    results = await apply_checkout_changes(
        checkout_entity,
        registration_entities,
        access_codes,
        event_stats,
        registration_service,
        account_service,
        hook_sender,
    )
    checkout_entity.changes_applied = True
    return results


async def _assign_registration_numbers(
    cart_data: CartData,
    registration_entities: Iterable[RegistrationEntity],
    event_service: EventService,
):
    event_stats = await event_service.get_event_stats(cart_data.event_id, lock=True)
    assign_registration_numbers(event_stats, registration_entities)


def _make_checkout_update_response(
    checkout_result: PaymentServiceCheckout, checkout_entity: CheckoutEntity
):
    if checkout_result.is_open:
        return Response(
            200,
            content=Content(
                b"application/json",
                get_converter().dumps(
                    CheckoutResponse(
                        id=checkout_entity.id,
                        service=checkout_entity.service,
                        external_id=checkout_result.id,
                        data=checkout_result.response_data,
                    )
                ),
            ),
        )
    else:
        return Response(204)


async def _validate_checkout_method(
    service: str,
    method: str,
    cart_data: CartData,
    pricing_result: PricingResult,
    checkout_service: CheckoutService,
):
    options = await checkout_service.get_checkout_methods_for_cart(
        cart_data, pricing_result
    )
    return any(o.service == service and o.method == method for o in options)


@allow_anonymous()
@app.router.get("/receipts/{receipt_id}")
@docs_helper(
    response_type=PricingResultResponse,
    response_summary="The receipt data",
    tags=["Checkout"],
)
async def get_receipt(
    receipt_id: str,
    service: CheckoutService,
    config: Config,
) -> PricingResultResponse:
    """Get receipt information by ID."""
    checkout = check_not_found(await service.get_checkout_by_receipt_id(receipt_id))

    assert checkout.receipt_id is not None
    receipt_url = _make_receipt_url(checkout.receipt_id, config)

    return PricingResultResponse.create(
        checkout.get_pricing_result(),
        receipt_url=receipt_url,
        date=checkout.date_closed,
    )


def _make_receipt_url(receipt_id: str, config: Config) -> str:
    url = config.payment.receipt_base_url
    if not url.endswith("/"):
        url += "/"

    return url + receipt_id
