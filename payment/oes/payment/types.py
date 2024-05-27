"""Type declarations."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias, runtime_checkable

if TYPE_CHECKING:
    from oes.payment.payment import (
        CancelPaymentRequest,
        CreatePaymentRequest,
        ParsedWebhook,
        PaymentMethodConfig,
        PaymentResult,
        UpdatePaymentRequest,
        WebhookRequest,
        WebhookUpdateRequest,
    )


CartData: TypeAlias = Mapping[str, Any]


class PaymentMethod(Protocol):
    """A payment method."""

    @abstractmethod
    async def create_payment(self, request: CreatePaymentRequest, /) -> PaymentResult:
        """Create a payment."""
        ...


class PaymentService(Protocol):
    """A payment service."""

    @abstractmethod
    def get_payment_method(self, config: PaymentMethodConfig, /) -> PaymentMethod:
        """Get a :class:`PaymentMethod`."""
        ...

    @abstractmethod
    async def cancel_payment(self, request: CancelPaymentRequest, /) -> PaymentResult:
        """Cancel a payment."""
        ...


@runtime_checkable
class UpdatablePaymentService(PaymentService, Protocol):
    """A client-updatable payment service."""

    @abstractmethod
    async def update_payment(self, request: UpdatePaymentRequest, /) -> PaymentResult:
        """Update a payment."""
        ...


class WebhookPaymentService(PaymentService, Protocol):
    """A payment service that receives webhooks."""

    @abstractmethod
    def parse_webhook(self, request: WebhookRequest, /) -> ParsedWebhook:
        """Parse a webhook."""
        ...

    @abstractmethod
    async def handle_webhook(self, request: WebhookUpdateRequest, /) -> PaymentResult:
        """Handle a webhook."""
        ...
