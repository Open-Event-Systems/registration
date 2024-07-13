"""Payment objects."""

from datetime import datetime
from enum import Enum
from typing import Any, Mapping

from attrs import field, frozen
from oes.payment.orm import Base
from oes.payment.pricing import PricingResult
from oes.payment.types import CartData
from oes.utils.logic import WhenCondition
from oes.utils.orm import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class PaymentStatus(str, Enum):
    """Payment status codes."""

    pending = "pending"
    completed = "completed"
    canceled = "canceled"


class PaymentMethodError(ValueError):
    """An error with processing a payment."""

    pass


class PaymentNotFoundError(ValueError):
    """Payment is not found."""

    pass


class PaymentServiceUnsupported(PaymentMethodError):
    """Raised when a payment service is not found/not supported."""

    pass


class PaymentStateError(PaymentMethodError):
    """Raised when a payment is in an invalid state."""

    pass


class PaymentError(PaymentMethodError):
    """An error with payment."""

    pass


@frozen
class PaymentOption:
    """A payment method option."""

    id: str
    name: str


@frozen
class PaymentMethodConfig:
    """Payment method configuration."""

    service: str
    name: str
    options: Mapping[str, Any] = field(factory=dict)
    when: WhenCondition = True


@frozen
class CreatePaymentRequest:
    """Information to create a payment."""

    id: str
    service: str
    cart_id: str
    cart_data: CartData
    pricing_result: PricingResult
    email: str | None


@frozen
class UpdatePaymentRequest:
    """Information to update a payment."""

    id: str
    service: str
    external_id: str
    data: Mapping[str, Any] = field(factory=dict)
    body: Mapping[str, Any] = field(factory=dict)


@frozen
class CancelPaymentRequest:
    """Information to cancel a payment."""

    id: str
    service: str
    external_id: str
    data: Mapping[str, Any] = field(factory=dict)


@frozen
class WebhookRequest:
    """Information about handling a webhook."""

    url: str
    headers: Mapping[str, Any]
    body: bytes


@frozen
class ParsedWebhook:
    """A parsed webhook request."""

    service: str
    external_id: str
    body: Mapping[str, Any]


@frozen
class WebhookUpdateRequest:
    """An update request from a parsed webhook."""

    id: str
    service: str
    external_id: str
    body: Mapping[str, Any]


@frozen
class PaymentResult:
    """Payment result object."""

    id: str
    service: str
    external_id: str
    status: PaymentStatus
    date_created: datetime = field(factory=lambda: datetime.now().astimezone())
    date_closed: datetime | None = None
    data: Mapping[str, Any] = field(factory=dict)
    body: Mapping[str, Any] = field(factory=dict)


class Payment(Base):
    """Payment entity."""

    __tablename__ = "payment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    service: Mapped[str]
    external_id: Mapped[str]
    status: Mapped[PaymentStatus] = mapped_column(String(16))
    cart_id: Mapped[str]
    cart_data: Mapped[JSON]
    pricing_result: Mapped[JSON]
    date_created: Mapped[datetime]
    date_closed: Mapped[datetime | None] = mapped_column(default=None)
    data: Mapped[JSON] = mapped_column(default_factory=dict)
