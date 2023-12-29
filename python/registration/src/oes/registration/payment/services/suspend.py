"""Payment service that implements transaction suspend/recall."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from oes.registration.checkout.entities import CheckoutState
from oes.registration.checkout.models import PaymentServiceCheckout
from oes.registration.payment.types import CheckoutData, PaymentService
from oes.util import get_now

if TYPE_CHECKING:
    from oes.registration.payment.models import CreateCheckoutRequest


class SuspendPaymentService(PaymentService):
    """Suspend payment service."""

    @property
    def id(self) -> str:
        """The payment method ID."""
        return "suspend"

    @property
    def name(self) -> str:
        """The human-readable service name."""
        return "Suspend"

    def get_url(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> Optional[str]:
        """URL unsupported."""
        return None

    async def create_checkout(
        self, request: CreateCheckoutRequest, checkout_id: Optional[UUID] = None, /
    ) -> PaymentServiceCheckout:
        """Create a suspended checkout."""
        return PaymentServiceCheckout(
            service=self.id,
            id=str(uuid.uuid4()),
            state=CheckoutState.pending,
            date_created=get_now(),
            checkout_data={},
            response_data={},
        )

    async def get_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> Optional[PaymentServiceCheckout]:
        """Return a canceled checkout."""
        return PaymentServiceCheckout(
            service=self.id,
            id=id,
            state=CheckoutState.canceled,
        )

    async def cancel_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> PaymentServiceCheckout:
        """Return a canceled checkout."""
        return PaymentServiceCheckout(
            service=self.id,
            id=id,
            state=CheckoutState.canceled,
        )
