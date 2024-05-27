"""Service objects."""

from collections.abc import Iterable
from typing import Any, Mapping

import nanoid
from cattrs import Converter
from oes.payment.config import Config
from oes.payment.payment import (
    CancelPaymentRequest,
    CreatePaymentRequest,
    Payment,
    PaymentMethodConfig,
    PaymentResult,
    PaymentServiceUnsupported,
    UpdatePaymentRequest,
)
from oes.payment.pricing import PricingResult
from oes.payment.types import CartData, PaymentService, UpdatablePaymentService
from oes.utils.logic import evaluate
from oes.utils.orm import Repo


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
        self.converter = converter

    def get_service(self, service: str) -> PaymentService | None:
        """Get a service by ID."""
        return self._services.get(service)

    def get_methods(
        self, cart_data: CartData, pricing_result: PricingResult
    ) -> Iterable[tuple[str, PaymentMethodConfig]]:
        """Get the available :class:`PaymentMethodConfig` objects."""
        ctx = {
            "cart": cart_data,
            "pricing_result": self.converter.unstructure(pricing_result),
        }
        for method_id, method in self.config.methods.items():
            if evaluate(method.when, ctx):
                yield method_id, method


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
