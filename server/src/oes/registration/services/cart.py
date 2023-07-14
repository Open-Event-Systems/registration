"""Cart service."""
import asyncio
from collections.abc import Mapping
from inspect import iscoroutinefunction
from typing import Optional
from uuid import UUID

from oes.registration.access_code.entities import AccessCodeEntity
from oes.registration.access_code.service import AccessCodeService
from oes.registration.auth.account_service import AccountService
from oes.registration.entities.cart import CartEntity
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.hook.models import HookConfig, HookEvent
from oes.registration.hook.service import HookSender
from oes.registration.models.cart import CartData, CartRegistration
from oes.registration.models.config import Config
from oes.registration.models.event import Event, SimpleEventInfo
from oes.registration.models.pricing import (
    PricingEventBody,
    PricingRequest,
    PricingResult,
)
from oes.registration.pricing import default_pricing
from oes.registration.serialization import get_converter
from oes.registration.services.registration import (
    RegistrationService,
    add_account_to_registration,
)
from sqlalchemy.ext.asyncio import AsyncSession


class CartService:
    """Cart service."""

    def __init__(self, db: AsyncSession, config: Config):
        self.db = db
        self.hook_config = config.hooks

    async def get_cart(self, id: str) -> Optional[CartEntity]:
        """Get a cart by its ID."""
        return await self.db.get(CartEntity, id)

    async def get_empty_cart(self, event_id: str) -> CartEntity:
        """Get the empty cart."""
        data = CartData(event_id=event_id)
        entity = CartEntity.create(data)
        saved = await self.save_cart(entity)
        return saved

    async def save_cart(self, cart: CartEntity) -> CartEntity:
        """Save a cart.

        Returns:
            The updated :class:`CartEntity`.
        """
        merged = await self.db.merge(cart)
        return merged


async def price_cart(
    cart_data: CartData,
    currency: str,
    event: Event,
    hook_config: HookConfig,
) -> PricingResult:
    """Price a cart, calling all pricing hooks.

    Args:
        cart_data: The :class:`CartData`.
        currency: The currency.
        event: The :class:`Event`.
        hook_config: The :class:`HookConfig`.

    Returns:
        The final :class:`PricingResult`.
    """
    req = PricingRequest(
        currency=currency,
        event=SimpleEventInfo.create(event),
        cart=cart_data,
    )
    initial_result = await default_pricing(event, req)
    return await _call_pricing_hooks(req, initial_result, hook_config)


async def _call_pricing_hooks(
    request: PricingRequest,
    result: PricingResult,
    hook_config: HookConfig,
) -> PricingResult:
    """Call all pricing hooks in order."""
    cur_result = result
    for hook_entry in hook_config.get_by_event(HookEvent.cart_price):
        hook = hook_entry.get_hook()
        body = PricingEventBody(
            request=request,
            prev_result=cur_result,
        )
        body_dict = get_converter().unstructure(body)
        if iscoroutinefunction(hook):
            result_dict = await hook(body_dict)
        else:
            loop = asyncio.get_running_loop()
            result_dict = await loop.run_in_executor(None, hook, body_dict)
        cur_result = get_converter().structure(result_dict, PricingResult)

    return cur_result


_err_out_of_date = (
    "This registration has changed. Please remove it and make your changes again."
)

_err_access_code = (
    "The access code is no longer valid. Please remove it and make your changes again."
)


def validate_changes(
    cart_data: CartData,
    registration_entities: Mapping[UUID, RegistrationEntity],
    access_codes: Mapping[str, AccessCodeEntity],
) -> Mapping[UUID, str]:
    """Validate that cart changes can be applied.

    Args:
        cart_data: The :class:`CartData`.
        registration_entities: A mapping of IDs to :class:`RegistrationEntity`.
        access_codes: A mapping of access codes to :class:`AccessCodeEntity`.

    Returns:
        A mapping of registration IDs to error messages.
    """
    errors = {}

    for cart_registration in cart_data.registrations:
        entity = registration_entities.get(cart_registration.id)
        if entity and not entity.validate_changes_from_cart(cart_registration):
            errors[cart_registration.id] = _err_out_of_date

        if not _validate_access_code(cart_registration, access_codes):
            errors[cart_registration.id] = _err_access_code

    return errors


def _validate_access_code(
    cart_registration: CartRegistration,
    access_codes: Mapping[str, AccessCodeEntity],
) -> bool:
    if cart_registration.access_code is not None:
        access_code = access_codes.get(cart_registration.access_code)
        if not access_code or not access_code.check_valid():
            return False
    return True


async def get_registration_entities_from_cart(
    cart_data: CartData,
    registration_service: RegistrationService,
    *,
    lock: bool = False,
) -> Mapping[UUID, Optional[RegistrationEntity]]:
    """Get the :class:`RegistrationEntity` for each registration in a cart.

    Args:
        cart_data: The :class:`CartData`.
        registration_service: The :class:`RegistrationService`.
        lock: Whether to lock tne entities.

    Returns:
        A mapping of registration IDs to entities.
    """
    results = {}

    registrations = await registration_service.get_registrations(
        (cr.id for cr in cart_data.registrations), lock=lock
    )
    for entity in registrations:
        results[entity.id] = entity

    return results


async def get_access_codes_from_cart(
    cart_data: CartData,
    access_code_service: AccessCodeService,
    *,
    lock: bool = False,
) -> Mapping[str, AccessCodeEntity]:
    """Get the :class:`AccessCodeEntity` instances used in a cart."""
    codes = sorted(
        cr.access_code for cr in cart_data.registrations if cr.access_code is not None
    )

    results = {}

    for code in codes:
        entity = await access_code_service.get_access_code(code, lock=lock)
        if entity:
            results[code] = entity

    return results


async def apply_changes(
    cart_data: CartData,
    registration_entities: Mapping[UUID, RegistrationEntity],
    access_codes: Mapping[str, AccessCodeEntity],
    registration_service: RegistrationService,
    account_service: AccountService,
    hook_sender: HookSender,
) -> list[RegistrationEntity]:
    """Apply changes from a cart.

    The changes must have already been validated.

    Marks access codes as used.

    Schedules hooks for registration creation/update.

    Args:
        cart_data: The :class:`CartData` to apply.
        registration_entities: A mapping of registration IDs to entities.
        access_codes: A mapping of access codes to entities.
        registration_service: The registration service.
        account_service: The account service.
        hook_sender: A :class:`HookSender` instance.

    Returns:
        A list of created/updated :class:`RegistrationEntity`.
    """
    results = []

    # update each registration, or create it if it doesn't exist
    for cart_registration in cart_data.registrations:
        entity = await _create_or_update_registration(
            cart_registration,
            registration_entities,
            registration_service,
            account_service,
            hook_sender,
        )

        results.append(entity)

        _mark_access_code_used(cart_registration, access_codes)

    return results


async def _create_or_update_registration(
    cart_registration: CartRegistration,
    registration_entities: Mapping[UUID, RegistrationEntity],
    registration_service: RegistrationService,
    account_service: AccountService,
    hook_sender: HookSender,
) -> RegistrationEntity:
    entity = registration_entities.get(cart_registration.id)
    if entity:
        await entity.apply_changes_from_cart(cart_registration, hook_sender)
    else:
        entity = RegistrationEntity.create_from_cart(cart_registration)
        await registration_service.create_registration(entity)
        await _add_account(cart_registration, entity, account_service)

    return entity


def _mark_access_code_used(
    cart_registration: CartRegistration,
    access_codes: Mapping[str, AccessCodeEntity],
):
    if cart_registration.access_code is not None:
        access_code = access_codes[cart_registration.access_code]
        access_code.used = True


async def _add_account(
    cart_registration: CartRegistration,
    entity: RegistrationEntity,
    service: AccountService,
):
    """Associate the registration with the account ID in the metadata."""
    meta = cart_registration.meta or {}
    account_id = meta.get("account_id")

    if account_id:
        await add_account_to_registration(UUID(account_id), entity, service)
