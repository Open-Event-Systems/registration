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
        Payment,
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

    @property
    @abstractmethod
    def name(self) -> str:
        """The service name."""
        ...

    @abstractmethod
    def get_payment_method(self, config: PaymentMethodConfig, /) -> PaymentMethod:
        """Get a :class:`PaymentMethod`."""
        ...

    @abstractmethod
    async def cancel_payment(self, request: CancelPaymentRequest, /) -> PaymentResult:
        """Cancel a payment."""
        ...


@runtime_checkable
class PaymentInfoURLService(Protocol):
    """A payment service that can provide a link to payment info."""

    @abstractmethod
    def get_payment_info_url(self, payment: Payment, /) -> str | None:
        """Get the URL of a payment."""
        ...


@runtime_checkable
class UpdatablePaymentService(PaymentService, Protocol):
    """A client-updatable payment service."""

    @abstractmethod
    async def update_payment(self, request: UpdatePaymentRequest, /) -> PaymentResult:
        """Update a payment."""
        ...


@runtime_checkable
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
