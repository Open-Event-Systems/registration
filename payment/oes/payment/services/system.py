"""System payment service."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import nanoid
from cattrs import Converter
from oes.payment.payment import (
    CancelPaymentRequest,
    CreatePaymentRequest,
    PaymentMethodConfig,
    PaymentMethodError,
    PaymentResult,
    PaymentStatus,
    UpdatePaymentRequest,
)
from oes.payment.types import PaymentMethod


class SystemPaymentService:
    """System payment service."""

    id = "system"

    def get_payment_method(self, config: PaymentMethodConfig) -> PaymentMethod:
        """Get the payment method."""
        return ZeroBalancePaymentMethod()

    async def update_payment(self, request: UpdatePaymentRequest, /) -> PaymentResult:
        """Update a payment."""
        cur_state = PaymentStatus(request.data.get("status", "pending"))
        date_closed_str = request.data.get("date_closed")
        date_closed = (
            datetime.fromisoformat(date_closed_str) if date_closed_str else None
        )
        if cur_state in (PaymentStatus.completed, PaymentStatus.canceled):
            return PaymentResult(
                id=request.id,
                service=self.id,
                external_id=request.external_id,
                status=cur_state,
                date_closed=date_closed,
                data=request.data,
            )

        date_closed = datetime.now().astimezone()

        return PaymentResult(
            id=request.id,
            service=self.id,
            external_id=request.external_id,
            status=PaymentStatus.completed,
            date_closed=date_closed,
            data={
                **request.data,
                "status": PaymentStatus.completed,
                "date_closed": date_closed.isoformat(),
            },
        )

    async def cancel_payment(self, request: CancelPaymentRequest) -> PaymentResult:
        """Cancel a payment."""
        cur_state = PaymentStatus(request.data.get("status", "pending"))
        date_closed_str = request.data.get("date_closed")
        date_closed = (
            datetime.fromisoformat(date_closed_str) if date_closed_str else None
        )
        if cur_state in (PaymentStatus.completed, PaymentStatus.canceled):
            return PaymentResult(
                id=request.id,
                service=self.id,
                external_id=request.external_id,
                status=cur_state,
                date_closed=date_closed,
                data=request.data,
            )

        date_closed = datetime.now().astimezone()

        return PaymentResult(
            id=request.id,
            service=self.id,
            external_id=request.external_id,
            status=PaymentStatus.canceled,
            date_closed=date_closed,
            data={
                **request.data,
                "status": PaymentStatus.canceled,
                "date_closed": date_closed.isoformat(),
            },
        )


class ZeroBalancePaymentMethod:
    """Zero balance payment method."""

    async def create_payment(self, request: CreatePaymentRequest, /) -> PaymentResult:
        """Create a payment."""
        if request.pricing_result.total_price != 0:
            raise PaymentMethodError("Balance is not 0")

        ext_id = nanoid.generate(size=14)
        return PaymentResult(
            id=request.id,
            service=SystemPaymentService.id,
            external_id=ext_id,
            status=PaymentStatus.pending,
            date_created=datetime.now().astimezone(),
            data={
                "status": PaymentStatus.pending.value,
            },
        )


def make_system_payment_service(
    config: Mapping[str, Any], converter: Converter
) -> SystemPaymentService:
    """Create a system payment service."""
    return SystemPaymentService()
