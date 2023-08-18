"""Checkout models."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from attrs import Factory, frozen
from oes.registration.cart.models import CartData, PricingResult
from oes.registration.checkout.entities import CheckoutEntity, CheckoutState
from typing_extensions import Self


@frozen
class PaymentServiceCheckout:
    """Checkout data."""

    service: str
    """The payment service ID."""

    id: str
    """The checkout ID in the payment service."""

    state: CheckoutState
    """The state of the checkout."""

    date_created: Optional[datetime] = None
    """The date the checkout was created with the service."""

    date_closed: Optional[datetime] = None
    """The date the checkout was closed with the service."""

    checkout_data: dict[str, Any] = Factory(dict)
    """Additional checkout data with the service."""

    response_data: dict[str, Any] = Factory(dict)
    """Additional checkout data with the service that will not be stored."""

    @property
    def is_open(self) -> bool:
        """Whether the checkout is open."""
        return self.state == CheckoutState.pending

    @property
    def is_closed(self) -> bool:
        """Whether the checkout is closed/canceled."""
        return self.state != CheckoutState.pending


@frozen
class CheckoutHookBody:
    """Body of a checkout event hook."""

    service: str
    id: UUID
    state: CheckoutState
    cart_id: str
    cart_data: CartData
    pricing_result: PricingResult
    external_id: str
    date_created: Optional[datetime] = None
    date_closed: Optional[datetime] = None
    external_data: dict[str, Any] = Factory(dict)
    receipt_id: Optional[str] = None

    @classmethod
    def create(cls, entity: CheckoutEntity) -> Self:
        """Create a :class:`CheckoutHookBody`."""
        return cls(
            service=entity.service,
            id=entity.id,
            state=entity.state,
            cart_id=entity.cart_id,
            cart_data=entity.get_cart_data(),
            pricing_result=entity.get_pricing_result(),
            external_id=entity.external_id,
            date_created=entity.date_created,
            date_closed=entity.date_closed,
            external_data=entity.external_data,
            receipt_id=entity.receipt_id,
        )
