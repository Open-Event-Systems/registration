"""Type declarations."""
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from oes.registration.models.logic import WhenCondition
from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from oes.registration.checkout.models import PaymentServiceCheckout
    from oes.registration.payment.models import (
        CreateCheckoutRequest,
        UpdateRequest,
        WebhookRequestInfo,
        WebhookResult,
    )

CheckoutData: TypeAlias = Mapping[str, Any]
"""Payment service specific data associated with a checkout."""


class PaymentMethodConfigBase(Protocol):
    """Base properties of a payment method configuration."""

    @property
    @abstractmethod
    def id(self) -> str:
        """The payment method ID."""
        ...

    @property
    @abstractmethod
    def service(self) -> str:
        """The service ID."""
        ...

    @property
    @abstractmethod
    def name(self) -> Optional[str]:
        """A human-readable name for the payment method."""
        ...

    @property
    @abstractmethod
    def when(self) -> WhenCondition:
        """The ``when`` condition."""
        ...


class PaymentService(Protocol):
    """Payment service interface."""

    @property
    @abstractmethod
    def id(self) -> str:
        """The payment service ID."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """The human-readable service name."""
        ...

    def get_url(
        self,
        id: str,
        /,
        *,
        checkout_data: Optional[CheckoutData] = None,
    ) -> Optional[str]:
        """Get a URL for a page describing the transaction."""
        return None

    @abstractmethod
    async def create_checkout(
        self,
        request: CreateCheckoutRequest,
        checkout_id: Optional[UUID] = None,
        /,
    ) -> PaymentServiceCheckout:
        """Create a checkout with the payment service.

        Args:
            request: A :class:`CreateCheckoutRequest` instance.
            checkout_id: The checkout ID.

        Raises:
            ValidationError: if the submitted data is not valid.

        Returns:
            A :class:`PaymentServiceCheckout`.
        """
        ...

    @abstractmethod
    async def get_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> Optional[PaymentServiceCheckout]:
        """Get the :class:`PaymentServiceCheckout` data for a checkout.

        Args:
            id: The checkout ID in the payment service.
            checkout_data: Additional checkout data.

        Returns:
            The current :class:`PaymentServiceCheckout`, or None if not found.
        """
        ...

    @abstractmethod
    async def cancel_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> PaymentServiceCheckout:
        """Cancel a checkout.

        Args:
            id: The checkout ID.
            checkout_data: Additional checkout data.

        Returns:
            An updated :class:`PaymentServiceCheckout` instance.

        Raises:
            CheckoutNotFoundError: if the checkout could not be found.
            CheckoutStateError: if the checkout could not be canceled.
        """
        ...


@runtime_checkable
class CheckoutUpdater(Protocol):
    """A payment service that receives updates directly from the client."""

    @abstractmethod
    async def update_checkout(
        self, update_request: UpdateRequest, /
    ) -> PaymentServiceCheckout:
        """Update a checkout.

        Args:
            update_request: A :class:`UpdateRequest` object.

        Returns:
            An updated :class:`PaymentServiceCheckout`.

        Raises:
            ValidationError: if the submitted checkout data is not valid.
            CheckoutStateError: if the checkout is in an invalid state.
            CheckoutNotFoundError: if the checkout is not found.
        """
        ...


@runtime_checkable
class WebhookHandler(Protocol):
    """A payment service that receives webhook updates."""

    @abstractmethod
    async def handle_webhook(
        self, request_info: WebhookRequestInfo, /
    ) -> WebhookResult:
        """Handle a webhook.

        Args:
            request_info: A :class:`WebhookRequestInfo` object describing the request.

        Returns:
            A :class:`WebhookResult` object.

        Raises:
            ValidationError: if the webhook request is not valid.
        """
        ...
