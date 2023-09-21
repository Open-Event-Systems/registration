"""Cart models."""
from __future__ import annotations

import hashlib
import itertools
import json
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    Optional,
    Sequence,
    Union,
    overload,
)
from uuid import UUID

from attr import evolve, field, frozen
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.models.event import SimpleEventInfo
from oes.registration.models.registration import Registration
from oes.registration.serialization import get_converter

CART_HASH_SIZE = 64
"""The string length of a cart hash."""


class CartError(ValueError):
    """Raised when a cart operation cannot be completed."""

    pass


class InvalidChangeError(CartError):
    """Raised if a registration change cannot be applied."""

    id: UUID
    """The registration ID."""

    def __init__(self, id: UUID):
        super().__init__(id)
        self.id = id


class PricingError(ValueError):
    """Raised when there is a problem with a pricing result."""

    pass


@frozen(kw_only=True)
class CartRegistration:
    """Registration data in a cart."""

    id: UUID
    """The ID of this item in the cart."""

    submission_id: Optional[str] = None
    """Used to ensure form submissions are unique."""

    access_code: Optional[str] = None
    """The access code used with this cart item."""

    old_data: dict[str, Any] = {}
    """The old/current data."""

    new_data: dict[str, Any] = {}
    """The new/updated data."""

    meta: Optional[dict[str, Any]] = None
    """Optional metadata with this cart registration."""

    @classmethod
    def create(
        cls,
        old: Union[Registration, RegistrationEntity, None],
        new: Union[Registration, RegistrationEntity],
        *,
        submission_id: Optional[str] = None,
        access_code: Optional[str] = None,
        meta: Optional[dict[str, Any]] = None,
    ) -> CartRegistration:
        """Create a :class:`CartRegistration` from a registration."""
        return cls(
            id=new.id,
            old_data=_reg_to_data(old),
            new_data=_reg_to_data(new),
            access_code=access_code,
            meta=meta,
            submission_id=submission_id,
        )


def _reg_to_data(reg: Union[Registration, RegistrationEntity, None]) -> dict[str, Any]:
    if isinstance(reg, Registration):
        return get_converter().unstructure(reg)
    elif isinstance(reg, RegistrationEntity):
        return get_converter().unstructure(reg.get_model())
    else:
        return {}


@frozen(kw_only=True)
class CartData:
    """Cart data class."""

    event_id: str
    """The event ID."""

    registrations: Sequence[CartRegistration] = ()
    """The registrations in the cart."""

    meta: Optional[dict[str, Any]] = None
    """Optional metadata about this cart."""

    def get_hash(self) -> str:
        """Get a hash of the cart data."""
        data = get_converter().unstructure(self)

        # use normal json so we can sort keys for consistent hashing
        # hacky
        from oes.registration.serialization.json import json_default

        data_bytes = json.dumps(data, default=json_default, sort_keys=True).encode()
        h = hashlib.new("sha256")
        h.update(data_bytes)
        hash_ = h.hexdigest()
        return hash_

    def add_registration(self, cart_registration: CartRegistration) -> CartData:
        """Add a :class:`CartRegistration` to this cart.

        Args:
            cart_registration: The new :class:`CartRegistration`.

        Returns:
            A new :class:`CartData` with the added registration.

        Raises:
            CartError: If the registration, submission ID, or access code is already
                in the cart, or if the registration belongs to a different event.
        """
        if cart_registration.id in [cr.id for cr in self.registrations]:
            raise CartError(
                f"Registration {cart_registration.id} is already in this cart"
            )

        if (
            cart_registration.submission_id is not None
            and cart_registration.submission_id
            in [
                cr.submission_id
                for cr in self.registrations
                if cr.submission_id is not None
            ]
        ):
            raise CartError("Duplicate submission")

        if (
            cart_registration.access_code is not None
            and cart_registration.access_code
            in [
                cr.access_code
                for cr in self.registrations
                if cr.access_code is not None
            ]
        ):
            # this does not check if the access code is valid or is used in another
            # cart, that happens later
            raise CartError("Access code already used")

        event_id = cart_registration.new_data.get("event_id")
        if event_id is not None and event_id != self.event_id:
            raise CartError("Registration event_id does not match the cart")

        new_seq = (*self.registrations, cart_registration)
        return evolve(self, registrations=new_seq)

    @overload
    def remove_registration(self, reg: UUID) -> CartData:
        ...

    @overload
    def remove_registration(self, reg: CartRegistration) -> CartData:
        ...

    def remove_registration(self, reg: Union[UUID, CartRegistration]) -> CartData:
        """Remove a :class:`CartRegistration` from this cart.

        Args:
            reg: The :class:`CartRegistration` or ID to remove.

        Returns:
            A new :class:`CartData` with the registration removed.
        """
        reg_id = reg if isinstance(reg, UUID) else reg.id
        new_seq = tuple(cr for cr in self.registrations if cr.id != reg_id)
        return evolve(self, registrations=new_seq)

    def validate_changes_apply(
        self, registrations: Iterable[Union[Registration, RegistrationEntity]]
    ) -> list[UUID]:
        """Validate that the changes in this cart can still be applied.

        Compares the version of each change with that of its matching registration.

        Args:
            registrations: The current registrations.

        Returns:
            A list of the IDs that have a mismatched version.
        """
        version_map = {r.id: r.version for r in registrations}

        bad_ids = []

        for cr in self.registrations:
            old_version = cr.old_data.get("version")
            cur_version = version_map.get(cr.id)
            if old_version != cur_version:
                bad_ids.append(cr.id)

        return bad_ids


@frozen(kw_only=True)
class Modifier:
    """A line item modifier."""

    type_id: Optional[str] = None
    """A type ID for the modifier."""

    name: str
    """The modifier name."""

    amount: int
    """The amount."""


def _validate_price(a, i, v):
    if v < 0:
        raise PricingError("Price cannot be negative")


@frozen(kw_only=True)
class LineItem:
    """A line item."""

    type_id: Optional[str] = None
    """A type ID for the line item."""

    name: str
    """The name of the line item."""

    price: int = field(validator=_validate_price)
    """The line item base price."""

    total_price: int
    """The total price of the line item."""

    modifiers: Sequence[Modifier] = ()
    """Line item modifiers."""

    description: Optional[str] = None
    """A line item description."""

    meta: Optional[dict[str, Any]] = None
    """Line item metadata."""

    def _validate_total(self):
        """Validate that the ``total_price`` sums up correctly."""
        total = self.price
        for modifier in self.modifiers:
            total += modifier.amount

        # discounts cannot make the total negative
        if total < 0:
            total = 0

        if total != self.total_price:
            raise PricingError("Line item total price does not sum")

    def __attrs_post_init__(self):
        self._validate_total()


def _validate_line_item_count(a, i, v):
    if len(v) == 0:
        raise PricingError("Cart has no line items")


def _validate_registration_count(a, i, v):
    if len(v) == 0:
        raise PricingError("Cart has no registrations")


@frozen
class PricingResultRegistration:
    """Line items grouped by registration."""

    registration_id: UUID
    """The registration ID."""

    line_items: Sequence[LineItem] = field(validator=_validate_line_item_count)
    """The line items."""

    name: Optional[str] = None
    """The registration name."""


@frozen
class PricingResult:
    """A cart pricing result."""

    currency: str
    """The currency code."""

    registrations: Sequence[PricingResultRegistration] = field(
        validator=_validate_registration_count
    )
    """The line items in the cart."""

    total_price: int
    """The cart total price."""

    modifiers: Sequence[Modifier] = ()
    """Cart-level modifiers."""

    def _validate_total(self):
        """Validate that the ``total_price`` sums up correctly."""
        total = sum(
            n.total_price
            for n in itertools.chain.from_iterable(
                r.line_items for r in self.registrations
            )
        )

        for mod in self.modifiers:
            total += mod.amount

        # discounts cannot make the total negative
        if total < 0:
            total = 0

        if total != self.total_price:
            raise PricingError("Cart total price does not sum")

    def __attrs_post_init__(self):
        self._validate_total()


def _get_added_option_ids(inst):
    old_ids = inst.old_data.get("option_ids", [])
    new_ids = inst.new_data.get("option_ids", [])

    return [o for o in new_ids if o not in old_ids]


@frozen
class PricingRequest:
    """Cart data to be priced."""

    currency: str
    """The currency code."""

    event: SimpleEventInfo
    """Event data."""

    cart: CartData
    """The cart data."""


@frozen
class PricingEventBody:
    """The body sent with a :class:`HookEvent.cart_price` event."""

    request: PricingRequest
    prev_result: PricingResult


PricingFunction = Callable[
    [PricingRequest, Optional[PricingResult]], Awaitable[PricingResult]
]
"""Function to get a :class:`PricingResult` from a :class:`PricingRequest`."""
