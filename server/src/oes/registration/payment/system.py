"""System payment service."""
import uuid
from typing import Any, Iterable, Optional
from uuid import UUID

from oes.registration.checkout.entities import CheckoutState
from oes.registration.checkout.models import PaymentServiceCheckout
from oes.registration.payment.base import (
    CheckoutCancelError,
    CheckoutMethod,
    CheckoutMethodsRequest,
    CheckoutStateError,
    CreateCheckoutRequest,
    PaymentService,
    UpdateRequest,
)
from oes.registration.util import get_now


class SystemPaymentService(PaymentService):
    """System payment service."""

    id = "system"
    name = "System"

    async def get_checkout(
        self, id: str, extra_data: Optional[dict[str, Any]] = None
    ) -> Optional[PaymentServiceCheckout]:
        return self._get_checkout(id, extra_data)

    async def get_checkout_methods(
        self, request: CheckoutMethodsRequest
    ) -> Iterable[CheckoutMethod]:
        if request.pricing_result.total_price == 0:
            return [
                CheckoutMethod(
                    service=self.id, method="zero-balance", name="Complete Checkout"
                )
            ]
        else:
            return []

    async def create_checkout(
        self,
        request: CreateCheckoutRequest,
        checkout_id: Optional[UUID] = None,
    ) -> PaymentServiceCheckout:
        id_ = str(uuid.uuid4())
        return PaymentServiceCheckout(
            service=self.id,
            id=id_,
            state=CheckoutState.pending,
            date_created=get_now(),
            checkout_data={
                "state": CheckoutState.pending.value,
            },
        )

    async def cancel_checkout(
        self, id: str, extra_data: Optional[dict[str, Any]] = None
    ) -> PaymentServiceCheckout:
        checkout = self._get_checkout(id, extra_data)
        if checkout.state == CheckoutState.complete:
            raise CheckoutCancelError("Checkout is already complete")
        elif checkout.state == CheckoutState.canceled:
            return PaymentServiceCheckout(
                service=self.id,
                id=self.id,
                state=checkout.state,
                checkout_data=checkout.checkout_data,
            )
        else:
            return PaymentServiceCheckout(
                service=self.id,
                id=id,
                state=CheckoutState.canceled,
                date_closed=get_now(),
                checkout_data={
                    "state": CheckoutState.canceled.value,
                },
            )

    async def _update_handler(self, request: UpdateRequest) -> PaymentServiceCheckout:
        checkout = self._get_checkout(request.id, request.checkout_data)
        if checkout.state == CheckoutState.complete:
            raise CheckoutStateError("Checkout is already complete")
        elif checkout.state == CheckoutState.canceled:
            raise CheckoutCancelError("Checkout is canceled")

        return PaymentServiceCheckout(
            service=self.id,
            id=checkout.id,
            state=CheckoutState.complete,
            date_closed=get_now(),
            checkout_data={
                "state": CheckoutState.complete.value,
            },
        )

    update_handler = _update_handler

    def _get_checkout(
        self, id: str, extra_data: Optional[dict[str, Any]]
    ) -> PaymentServiceCheckout:
        extra_data = extra_data or {}
        state = CheckoutState(extra_data.get("state", CheckoutState.pending))
        return PaymentServiceCheckout(
            service=self.id, id=id, state=state, checkout_data={"state": state.value}
        )
