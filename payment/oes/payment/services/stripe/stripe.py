"""Stripe module."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from datetime import datetime
from typing import Any

from attrs import frozen
from cattrs import Converter
from oes.payment.payment import (
    CancelPaymentRequest,
    CreatePaymentRequest,
    PaymentMethodConfig,
    PaymentResult,
    PaymentStateError,
    PaymentStatus,
    UpdatePaymentRequest,
)
from oes.payment.types import CartData
from stripe import Customer, CustomerService, StripeClient
from stripe.checkout import SessionService


@frozen
class StripeConfig:
    """Stripe config."""

    publishable_key: str
    secret_key: str


@frozen
class StripePaymentBody:
    """Stripe payment body."""

    id: str
    publishable_key: str
    client_secret: str
    amount: int
    currency: str


class StripeService:
    """Stripe payment service."""

    name = "stripe"

    def __init__(self, publishable_key: str, secret_key: str, converter: Converter):
        self.publishable_key = publishable_key
        self.converter = converter
        self.stripe = StripeClient(api_key=secret_key)

    def get_payment_method(
        self, config: PaymentMethodConfig, /
    ) -> StripeCheckoutPaymentMethod:
        return StripeCheckoutPaymentMethod(
            self.publishable_key, self.converter, self.stripe
        )

    async def update_payment(self, request: UpdatePaymentRequest) -> PaymentResult:
        """Update a payment."""
        checkout = await self.stripe.checkout.sessions.retrieve_async(
            request.external_id
        )
        # TODO: handle not found

        if checkout.status == "open":
            status = PaymentStatus.pending
        elif checkout.status == "complete":
            status = PaymentStatus.completed
        else:
            raise PaymentStateError

        res = PaymentResult(
            id=request.id,
            service=request.service,
            external_id=checkout.id,
            date_created=datetime.fromtimestamp(checkout.created).astimezone(),
            status=status,
        )

        return res

    async def cancel_payment(self, request: CancelPaymentRequest, /) -> PaymentResult:
        """Cancel a payment."""
        res = await self.stripe.checkout.sessions.expire_async(request.external_id)
        # TODO: handle errors
        return PaymentResult(
            id=request.id,
            service=request.service,
            external_id=res.id,
            status=PaymentStatus.canceled,
            date_created=datetime.fromtimestamp(res.created).astimezone(),
        )


class StripeCheckoutPaymentMethod:
    """Stripe checkout payment method."""

    def __init__(
        self, publishable_key: str, converter: Converter, stripe: StripeClient
    ):
        self.publishable_key = publishable_key
        self.converter = converter
        self.stripe = stripe

    async def create_payment(self, request: CreatePaymentRequest) -> PaymentResult:
        """Create a payment."""
        cust_id = await self._get_or_create_customer(request)

        params: SessionService.CreateParams = {
            "currency": request.pricing_result.currency,
            "ui_mode": "custom",
            "mode": "payment",
        }

        if cust_id:
            params["customer"] = cust_id

        line_items: list[SessionService.CreateParamsLineItem] = []

        for reg in request.pricing_result.registrations:
            for pr_li in reg.line_items:
                li: SessionService.CreateParamsLineItem = {
                    "price_data": {
                        "currency": request.pricing_result.currency,
                        "product_data": {
                            "name": pr_li.name or "Registration",
                            "description": pr_li.description or "",
                        },
                        "unit_amount": request.pricing_result.total_price,
                    },
                    "quantity": 1,
                }
                line_items.append(li)

        params["line_items"] = line_items

        checkout = await self.stripe.checkout.sessions.create_async(params=params)

        assert checkout.client_secret

        body = StripePaymentBody(
            id=checkout.id,
            publishable_key=self.publishable_key,
            client_secret=checkout.client_secret,
            amount=request.pricing_result.total_price,
            currency=request.pricing_result.currency,
        )

        return PaymentResult(
            id=request.id,
            service=request.service,
            date_created=datetime.fromtimestamp(checkout.created).astimezone(),
            status=PaymentStatus.pending,
            external_id=checkout.id,
            body=self.converter.unstructure(body),
        )

    async def _get_or_create_customer(
        self, request: CreatePaymentRequest
    ) -> str | None:
        cart_cust = _cart_to_customer(request.cart_data) or {}
        email = cart_cust.get("email") if cart_cust else None
        existing = await self._get_customer(email) if email else None
        if existing:
            return existing.id
        return await self._create_customer(request)

    async def _create_customer(self, request: CreatePaymentRequest) -> str | None:
        cust = _cart_to_customer(request.cart_data)
        if not cust:
            return None

        res = await self.stripe.customers.create_async(params=cust)
        return res.id

    async def _get_customer(self, email: str) -> Customer | None:
        res = await self.stripe.customers.list_async(
            params={
                "email": email.strip().lower(),
            }
        )
        return next(iter(res.data), None)


def _cart_to_customer(cart_data: CartData) -> CustomerService.CreateParams | None:
    for reg in _get_cart_regs(cart_data):
        return _reg_to_customer(reg)


def _get_cart_regs(cart_data: CartData) -> Iterator[Mapping[str, Any]]:
    registrations = cart_data.get("registrations", [])
    for reg in registrations:
        yield reg.get("new", {})


def _reg_to_customer(data: Mapping[str, Any]) -> CustomerService.CreateParams:
    email = data.get("email", "")
    email = email.strip().lower()
    fname = data.get("first_name", "")
    lname = data.get("last_name", "")
    pname = data.get("preferred_name", "")
    parts = (n.strip() for n in (pname or fname, lname) if n.strip())
    joined = " ".join(parts)

    params: CustomerService.CreateParams = {}

    if email:
        params["email"] = email

    if joined:
        params["name"] = joined

    return params


def make_stripe_payment_service(
    config: Mapping[str, Any], converter: Converter
) -> StripeService:
    """Create a Square payment service."""
    stripe_config = converter.structure(config, StripeConfig)
    return StripeService(
        stripe_config.publishable_key, stripe_config.secret_key, converter
    )
