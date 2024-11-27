"""Mock payment service."""

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import nanoid
from cattrs import Converter
from oes.payment.currency import format_currency
from oes.payment.payment import (
    CancelPaymentRequest,
    CreatePaymentRequest,
    PaymentError,
    PaymentMethodConfig,
    PaymentResult,
    PaymentStatus,
    UpdatePaymentRequest,
)
from typing_extensions import Self


class MockPaymentService:
    """Mock payment service."""

    id = "mock"
    name = "Mock"

    def get_payment_method(self, config: PaymentMethodConfig) -> Self:
        """Get the payment method."""
        return self

    async def create_payment(self, request: CreatePaymentRequest, /) -> PaymentResult:
        """Create a payment."""
        ext_id = nanoid.generate(size=14)
        currency = request.pricing_result.currency
        total_price = request.pricing_result.total_price
        return PaymentResult(
            id=request.id,
            service=self.id,
            external_id=ext_id,
            status=PaymentStatus.pending,
            date_created=datetime.now().astimezone(),
            data={
                "status": PaymentStatus.pending.value,
                "currency": currency,
                "total_price": total_price,
                "total_price_string": format_currency(currency, total_price),
            },
            body={
                "currency": currency,
                "total_price": total_price,
                "total_price_string": format_currency(currency, total_price),
            },
        )

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
                body={
                    "currency": request.data.get("currency"),
                    "total_price": request.data.get("total_price"),
                    "total_price_string": request.data.get("total_price_string"),
                },
            )

        card_number = request.body.get("card_number")
        if not isinstance(card_number, str) or not re.match(r"^[0-9-]+$", card_number):
            raise PaymentError("Invalid card")

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
            body={
                "currency": request.data.get("currency"),
                "total_price": request.data.get("total_price"),
                "total_price_string": request.data.get("total_price_string"),
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
                body={
                    "currency": request.data.get("currency"),
                    "total_price": request.data.get("total_price"),
                    "total_price_string": request.data.get("total_price_string"),
                },
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
            body={
                "currency": request.data.get("currency"),
                "total_price": request.data.get("total_price"),
                "total_price_string": request.data.get("total_price_string"),
            },
        )


def make_mock_payment_service(
    config: Mapping[str, Any], converter: Converter
) -> MockPaymentService:
    """Create a mock payment service."""
    return MockPaymentService()
