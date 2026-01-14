"""Suspend service."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import nanoid
from cattrs import Converter
from oes.payment.payment import (
    CancelPaymentRequest,
    CreatePaymentRequest,
    PaymentMethodConfig,
    PaymentResult,
    PaymentStatus,
)
from typing_extensions import Self


class SuspendPaymentService:
    """Suspend payment service."""

    id = "suspend"
    name = "Suspend"

    def __init__(self, config: Mapping[str, Any]):
        self.config = config

    def get_payment_method(self, config: PaymentMethodConfig) -> Self:
        """Get the payment method."""
        return self

    async def create_payment(self, request: CreatePaymentRequest, /) -> PaymentResult:
        """Create a payment."""
        ext_id = nanoid.generate(size=14)
        now = datetime.now().astimezone()

        return PaymentResult(
            id=request.id,
            service=self.id,
            external_id=ext_id,
            status=PaymentStatus.canceled,
            date_created=now,
            date_closed=now,
            data={"date_closed": now.isoformat()},
            body={"message": self.config.get("message")},
        )

    async def cancel_payment(self, request: CancelPaymentRequest) -> PaymentResult:
        """Cancel a payment."""
        date_closed_str = request.data.get("date_closed")
        date_closed = (
            datetime.fromisoformat(date_closed_str) if date_closed_str else None
        )

        return PaymentResult(
            id=request.id,
            service=self.id,
            external_id=request.external_id,
            status=PaymentStatus.canceled,
            date_closed=date_closed,
            data={
                "date_closed": date_closed.isoformat() if date_closed else None,
            },
            body={},
        )


def make_suspend_payment_service(
    config: Mapping[str, Any], converter: Converter
) -> SuspendPaymentService:
    """Create a suspend payment service."""
    return SuspendPaymentService(config)
