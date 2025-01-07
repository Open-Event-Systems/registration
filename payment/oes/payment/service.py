"""Service objects."""

from collections.abc import Iterable, Sequence
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
    PaymentStatus,
    UpdatePaymentRequest,
    make_receipt_id,
)
from oes.payment.pricing import PricingResult
from oes.payment.types import CartData, PaymentService, UpdatablePaymentService
from oes.utils.logic import evaluate
from oes.utils.orm import Repo
from sqlalchemy import ColumnElement, func, or_, select


class PaymentRepo(Repo[Payment, str]):
    """Payment repository."""

    entity_type = Payment

    async def get_by_receipt_id(self, receipt_id: str) -> Payment | None:
        """Get a payment by receipt ID."""
        q = select(Payment).where(Payment.receipt_id == receipt_id)
        res = await self.session.execute(q)
        return res.scalar()

    async def get_by_registration_id(
        self, event_id: str, registration_id: str
    ) -> Sequence[Payment]:
        """Get payments by registration ID."""
        q = select(Payment).where(
            Payment.cart_data.contains(
                {
                    "event_id": event_id,
                    "registrations": [
                        {
                            "id": registration_id,
                        }
                    ],
                }
            )
        )
        res = await self.session.execute(q)
        return res.scalars().all()

    async def get_suspended(self, event_id: str, q: str) -> Sequence[Payment]:
        """Search suspended checkouts."""
        query = (
            select(Payment)
            .where(Payment.service == "suspend")
            .where(Payment.cart_data.contains({"event_id": event_id}))
        )

        q = q.lower().strip()
        if q:
            query = query.where(_get_search(q))

        query.order_by(Payment.date_created.desc())
        query = query.limit(20)

        res = await self.session.execute(query)
        return res.scalars().all()


def _get_search(q: str) -> ColumnElement:
    exprs = or_(
        func.lower(
            Payment.cart_data["registrations"][0]["new"]["last_name"].as_string()
        ).startswith(q),
        func.lower(
            Payment.cart_data["registrations"][1]["new"]["last_name"].as_string()
        ).startswith(q),
        func.lower(
            Payment.cart_data["registrations"][2]["new"]["last_name"].as_string()
        ).startswith(q),
        func.lower(
            Payment.cart_data["registrations"][0]["new"]["email"].as_string()
        ).startswith(q),
        func.lower(
            Payment.cart_data["registrations"][1]["new"]["email"].as_string()
        ).startswith(q),
        func.lower(
            Payment.cart_data["registrations"][2]["new"]["email"].as_string()
        ).startswith(q),
    )
    return exprs


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
        self,
        cart_data: CartData,
        pricing_result: PricingResult,
        user_role: str | None,
    ) -> Iterable[tuple[str, PaymentMethodConfig]]:
        """Get the available :class:`PaymentMethodConfig` objects."""
        # return an empty tuple when the cart is empty
        if len(cart_data.get("registrations", [])) == 0:
            return ()
        ctx = {
            "user": {
                "role": user_role,
            },
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
        email: str | None,
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
            email=email,
        )
        result = await method_obj.create_payment(req)
        payment = Payment(
            id=result.id,
            service=result.service,
            external_id=result.external_id,
            receipt_id=None,
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

        # assign receipt ID
        if payment.receipt_id is None and payment.status == PaymentStatus.completed:
            payment.receipt_id = make_receipt_id()

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
