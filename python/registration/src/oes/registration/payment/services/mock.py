"""Mock payment service."""
import uuid
from collections.abc import Mapping
from typing import Optional
from uuid import UUID

from oes.registration.checkout.entities import CheckoutState
from oes.registration.checkout.models import PaymentServiceCheckout
from oes.registration.payment.errors import (
    CheckoutNotFoundError,
    CheckoutStateError,
    ValidationError,
)
from oes.registration.payment.models import CreateCheckoutRequest, UpdateRequest
from oes.registration.payment.types import CheckoutData, CheckoutUpdater, PaymentService
from oes.registration.serialization.common import structure_datetime
from oes.util import get_now


class MockPaymentService(PaymentService, CheckoutUpdater):
    """Mock payment service."""

    @property
    def id(self) -> str:
        return "mock"

    @property
    def name(self) -> str:
        return "Mock"

    async def create_checkout(
        self, request: CreateCheckoutRequest, checkout_id: Optional[UUID] = None, /
    ) -> PaymentServiceCheckout:
        id_ = str(uuid.uuid4())
        now = get_now()
        return PaymentServiceCheckout(
            service=self.id,
            id=id_,
            state=CheckoutState.pending,
            date_created=now,
            checkout_data={
                "date_created": now.isoformat(),
                "state": CheckoutState.pending.value,
            },
        )

    async def get_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> Optional[PaymentServiceCheckout]:
        if not checkout_data:
            return None
        return self._make_checkout(id, checkout_data)

    async def cancel_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> PaymentServiceCheckout:
        if not checkout_data:
            raise CheckoutNotFoundError

        state = CheckoutState(checkout_data.get("state", CheckoutState.pending))

        if state == CheckoutState.complete:
            raise CheckoutStateError("Checkout is already complete")

        updated = dict(checkout_data)
        updated["state"] = CheckoutState.canceled.value
        updated["date_closed"] = get_now().isoformat()
        return self._make_checkout(id, updated)

    async def update_checkout(
        self, update_request: UpdateRequest, /
    ) -> PaymentServiceCheckout:
        checkout = await self.get_checkout(
            update_request.id, checkout_data=update_request.checkout_data
        )
        if not checkout:
            raise CheckoutNotFoundError

        if checkout.state == CheckoutState.complete:
            raise CheckoutStateError("Checkout is already complete")
        elif checkout.state == CheckoutState.canceled:
            raise CheckoutStateError("Checkout is canceled")

        card = update_request.body.get("card")
        try:
            int(card)
        except (TypeError, ValueError):
            raise ValidationError("Invalid card")

        updated = dict(checkout.checkout_data)
        updated["date_closed"] = get_now().isoformat()
        updated["state"] = CheckoutState.complete.value

        return self._make_checkout(update_request.id, updated)

    def _make_checkout(
        self, id: str, checkout_data: CheckoutData
    ) -> PaymentServiceCheckout:
        state = CheckoutState(checkout_data.get("state", CheckoutState.pending.value))
        date_created = checkout_data.get("date_created")
        date_created = structure_datetime(date_created) if date_created else None
        date_closed = checkout_data.get("date_closed")
        date_closed = structure_datetime(date_closed) if date_closed else None
        return PaymentServiceCheckout(
            service=self.id,
            id=id,
            state=state,
            date_created=date_created,
            date_closed=date_closed,
            checkout_data=checkout_data,
        )


def create_mock_payment_service(config_data: Mapping) -> MockPaymentService:
    """Create a mock payment service."""
    return MockPaymentService()
