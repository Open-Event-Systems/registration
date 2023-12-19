"""Payment models."""
from collections.abc import Mapping
from typing import Optional

from attrs import Factory, frozen
from oes.registration.cart.models import CartData, PricingResult
from oes.registration.checkout.models import PaymentServiceCheckout
from oes.registration.payment.config import PaymentMethod
from oes.registration.payment.types import CheckoutData


@frozen(kw_only=True)
class CreateCheckoutRequest:
    """Request to create a checkout."""

    service: str
    """The service ID."""

    method: PaymentMethod
    """The payment method."""

    cart_data: CartData
    """The cart data."""

    pricing_result: PricingResult
    """The pricing result."""

    # TODO: email, other user info


@frozen(kw_only=True)
class UpdateRequest:
    """A checkout update request."""

    service: str
    """The service ID."""

    id: str
    """The ID of the checkout in the service."""

    checkout_data: CheckoutData = Factory(dict)
    """The external checkout data for the existing checkout."""

    body: CheckoutData = Factory(dict)
    """The data submitted by the client."""


@frozen
class WebhookRequestInfo:
    """Information about a webhook request."""

    body: bytes
    """The body bytes."""

    url: str
    """The request URL."""

    headers: Mapping[str, str]
    """The request headers."""


@frozen
class WebhookResult:
    """A webhook request result."""

    updated_checkout: Optional[PaymentServiceCheckout] = None
    """The updated checkout."""

    body: Optional[bytes] = None
    """The body bytes."""

    content_type: Optional[bytes] = None
    """The response content type."""

    status: int = 204
    """The response status."""
