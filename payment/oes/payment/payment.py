"""Payment objects."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping

import nanoid
from attrs import field, frozen, resolve_types
from cattrs import Converter
from oes.payment.orm import Base
from oes.payment.pricing import PricingResult
from oes.payment.types import CartData, PaymentService, UpdatablePaymentService
from oes.utils.logic import WhenCondition
from oes.utils.orm import JSON, Repo
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

if TYPE_CHECKING:
    from oes.payment.config import Config


class PaymentStatus(str, Enum):
    """Payment status codes."""

    pending = "pending"
    completed = "completed"
    canceled = "canceled"


class PaymentMethodError(ValueError):
    """An error with processing a payment."""

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
    service_id: str
    name: str


@frozen
class PaymentMethodConfig:
    """Payment method configuration."""

    service: str
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


class PaymentRepo(Repo[Payment, str]):
    """Payment repository."""

    entity_type = Payment


class PaymentServicesSvc:
    """Payment services service."""

    def __init__(self, config: Config, converter: Converter):
        from oes.payment.config import get_payment_service_factory

        self.config = config
        factories = {
            svc: get_payment_service_factory(svc) for svc in config.services.keys()
        }
        self._services = {
            svc: factories[svc](svc_cfg, converter)
            for svc, svc_cfg in config.services.items()
        }

    def get_service(self, service: str) -> PaymentService | None:
        """Get a service by ID."""
        return self._services.get(service)


class PaymentSvc:
    """Payment service."""

    def __init__(
        self, services: PaymentServicesSvc, repo: PaymentRepo, converter: Converter
    ):
        self.services = services
        self.repo = repo
        self.converter = converter

    async def create_payment(
        self,
        service: str,
        method: PaymentMethodConfig,
        cart_id: str,
        cart_data: CartData,
        pricing_result: PricingResult,
    ) -> PaymentResult:
        """Create a payment."""
        svc = self._get_service(service)
        method_obj = svc.get_payment_method(method)
        req = CreatePaymentRequest(
            id=nanoid.generate(size=14),
            service=service,
            cart_id=cart_id,
            cart_data=cart_data,
            pricing_result=pricing_result,
        )
        result = await method_obj.create_payment(req)
        payment = Payment(
            id=result.id,
            service=result.service,
            external_id=result.external_id,
            status=result.status,
            cart_id=cart_id,
            cart_data=dict(cart_data),
            pricing_result=self.converter.unstructure(pricing_result),
            date_created=result.date_created,
            date_closed=result.date_closed,
            data=dict(result.data),
        )
        self.repo.add(payment)
        return result

    async def update_payment(
        self, payment: Payment, body: Mapping[str, Any]
    ) -> PaymentResult:
        """Update a payment."""
        svc = self._get_service(payment.service)
        if not isinstance(svc, UpdatablePaymentService):
            raise PaymentServiceUnsupported
        req = UpdatePaymentRequest(
            id=payment.id,
            service=payment.service,
            external_id=payment.external_id,
            data=payment.data,
            body=body,
        )
        res = await svc.update_payment(req)
        payment.status = res.status
        payment.date_closed = res.date_closed
        payment.data = {**payment.data, **res.data}
        return res

    async def cancel_payment(self, payment: Payment) -> PaymentResult:
        """Cancel a payment."""
        svc = self._get_service(payment.service)
        req = CancelPaymentRequest(
            id=payment.id,
            service=payment.service,
            external_id=payment.external_id,
            data=payment.data,
        )
        res = await svc.cancel_payment(req)
        payment.status = res.status
        payment.date_closed = res.date_closed
        payment.data = {**payment.data, **res.data}
        return res

    def _get_service(self, service: str) -> PaymentService:
        svc = self.services.get_service(service)
        if not svc:
            raise PaymentServiceUnsupported
        return svc


resolve_types(PaymentMethodConfig)
