"""Stripe module."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from datetime import datetime
from typing import Any, Literal, cast

import stripe
from attrs import frozen
from cattrs import Converter
from oes.payment.payment import (
    CancelPaymentRequest,
    CreatePaymentRequest,
    ParsedWebhook,
    Payment,
    PaymentError,
    PaymentMethodConfig,
    PaymentMethodError,
    PaymentResult,
    PaymentStateError,
    PaymentStatus,
    UpdatePaymentRequest,
    WebhookRequest,
    WebhookUpdateRequest,
)
from oes.payment.types import CartData
from stripe import (
    Customer,
    CustomerService,
    PaymentIntentService,
    SignatureVerificationError,
    StripeClient,
)
from stripe.checkout import Session, SessionService


@frozen
class StripeConfig:
    """Stripe config."""

    publishable_key: str
    secret_key: str
    webhook_secret: str | None = None


@frozen
class StripeMethodOptions:
    """Stripe payment method options."""

    method: Literal["terminal", "checkout"] | None = None
    reader_id: str | None = None


@frozen
class StripeCheckoutPaymentBody:
    """Stripe checkout payment body."""

    type: Literal["checkout"]
    id: str
    publishable_key: str
    amount: int
    currency: str
    client_secret: str


@frozen
class StripeTerminalPaymentBody:
    """Stripe terminal payment body."""

    type: Literal["terminal"]


@frozen
class StripePaymentData:
    """Stripe payment data."""

    type: Literal["checkout", "terminal"] | None = None
    payment_id: str | None = None
    reader_id: str | None = None
    live_mode: bool | None = None


class StripeService:
    """Stripe payment service."""

    name = "stripe"

    def __init__(
        self,
        publishable_key: str,
        secret_key: str,
        webhook_secret: str,
        converter: Converter,
    ):
        self.publishable_key = publishable_key
        self.converter = converter
        self.stripe = StripeClient(api_key=secret_key)
        self._webhook_secret = webhook_secret

    def get_payment_method(
        self, config: PaymentMethodConfig, /
    ) -> StripeCheckoutPaymentMethod | StripeTerminalPaymentMethod:
        options = self.converter.structure(config.options, StripeMethodOptions)
        if options.method == "terminal":
            return StripeTerminalPaymentMethod(
                self.stripe,
                self.publishable_key,
                self.converter,
                options.reader_id or "",
            )
        elif options.method == "checkout" or options.method is None:
            return StripeCheckoutPaymentMethod(
                self.stripe, self.publishable_key, self.converter
            )
        else:
            raise PaymentError(f"Unknown payment type: {options.method}")

    def get_payment_info_url(self, payment: Payment, /) -> str | None:
        """Get the URL to a payment info page."""
        payment_id = payment.data.get("payment_id")
        live_mode = payment.data.get("live_mode")

        if not payment_id:
            return None
        elif live_mode:
            return f"https://dashboard.stripe.com/payments/{payment_id}"
        else:
            return f"https://dashboard.stripe.com/test/payments/{payment_id}"

    async def update_payment(self, request: UpdatePaymentRequest) -> PaymentResult:
        """Update a payment."""
        typ = request.data.get("type")
        if typ == "terminal":
            return await self._update_terminal(request)
        elif typ == "checkout" or typ is None:
            return await self._update_checkout(request)
        else:
            raise PaymentError(f"Unknown payment type: {typ}")

    async def _update_checkout(self, request: UpdatePaymentRequest) -> PaymentResult:
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

        payment_id = checkout.payment_intent
        live_mode = checkout.livemode

        res = PaymentResult(
            id=request.id,
            service=request.service,
            external_id=checkout.id,
            date_created=datetime.fromtimestamp(checkout.created).astimezone(),
            status=status,
            data={**request.data, "payment_id": payment_id, "live_mode": live_mode},
        )

        return res

    async def _update_terminal(self, request: UpdatePaymentRequest) -> PaymentResult:
        payment_intent = await self.stripe.payment_intents.retrieve_async(
            request.external_id
        )
        # TODO: handle not found

        if payment_intent.status == "succeeded":
            status = PaymentStatus.completed
        elif payment_intent.status == "canceled":
            status = PaymentStatus.canceled
        else:
            status = PaymentStatus.pending

        live_mode = payment_intent.livemode

        res = PaymentResult(
            id=request.id,
            service=request.service,
            external_id=payment_intent.id,
            date_created=datetime.fromtimestamp(payment_intent.created).astimezone(),
            status=status,
            data={**request.data, "payment_id": request.id, "live_mode": live_mode},
        )

        return res

    async def cancel_payment(self, request: CancelPaymentRequest, /) -> PaymentResult:
        """Cancel a payment."""
        typ = request.data.get("type")
        if typ == "terminal":
            res = await self.stripe.payment_intents.cancel_async(request.external_id)
            reader_id = request.data.get("reader_id")
            if reader_id:
                await self.stripe.terminal.readers.cancel_action_async(reader_id)
            return PaymentResult(
                id=request.id,
                service=request.service,
                external_id=res.id,
                status=PaymentStatus.canceled,
                date_created=datetime.fromtimestamp(res.created).astimezone(),
            )
        elif typ == "checkout" or typ is None:
            res = await self.stripe.checkout.sessions.expire_async(request.external_id)
            # TODO: handle errors
            return PaymentResult(
                id=request.id,
                service=request.service,
                external_id=res.id,
                status=PaymentStatus.canceled,
                date_created=datetime.fromtimestamp(res.created).astimezone(),
            )
        else:
            raise PaymentError(f"Unknown payment type: {typ}")

    def parse_webhook(self, request: WebhookRequest, /) -> ParsedWebhook:
        """Parse a webhook."""
        header = request.headers.get("stripe-signature", "")

        try:
            event = stripe.Webhook.construct_event(
                request.body, header, self._webhook_secret
            )
        except ValueError as e:
            raise PaymentMethodError("Invalid body") from e
        except SignatureVerificationError as e:
            raise PaymentMethodError("Invalid signature") from e

        if event.type == "checkout.session.completed":
            data = cast(Session, event.data.object)
            parsed = ParsedWebhook("stripe", data.id, data)
            return parsed
        else:
            raise PaymentMethodError("Unsupported event")

    async def handle_webhook(self, request: WebhookUpdateRequest, /) -> PaymentResult:
        """Handle a webhook."""
        data = Session.construct_from(dict(request.body), None)

        if data.status != "complete":
            raise PaymentStateError("Payment not complete")

        payment_id = data.payment_intent
        live_mode = data.livemode

        return PaymentResult(
            id=request.id,
            service=request.service,
            external_id=data.id,
            status=PaymentStatus.completed,
            date_closed=datetime.now().astimezone(),
            date_created=datetime.fromtimestamp(data.created).astimezone(),
            data={"payment_id": payment_id, "live_mode": live_mode},
        )


class _StripeCustomerHandler:
    """Customer creation."""

    def __init__(self, stripe: StripeClient):
        self.stripe = stripe

    async def get_or_create_customer(self, request: CreatePaymentRequest) -> str | None:
        """Get or create a customer from a payment."""
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


class StripeCheckoutPaymentMethod:
    """Stripe checkout payment method."""

    def __init__(
        self, stripe: StripeClient, publishable_key: str, converter: Converter
    ):
        self.stripe = stripe
        self.publishable_key = publishable_key
        self.converter = converter
        self._customer = _StripeCustomerHandler(stripe)

    async def create_payment(self, request: CreatePaymentRequest) -> PaymentResult:
        """Create a payment."""
        cust_id = await self._customer.get_or_create_customer(request)

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
                        "unit_amount": pr_li.total_price,
                    },
                    "quantity": 1,
                }
                line_items.append(li)

        params["line_items"] = line_items

        checkout = await self.stripe.checkout.sessions.create_async(params=params)

        assert checkout.client_secret

        body = StripeCheckoutPaymentBody(
            type="checkout",
            id=checkout.id,
            publishable_key=self.publishable_key,
            client_secret=checkout.client_secret,
            amount=request.pricing_result.total_price,
            currency=request.pricing_result.currency,
        )

        data = StripePaymentData(
            type="checkout",
        )

        return PaymentResult(
            id=request.id,
            service=request.service,
            date_created=datetime.fromtimestamp(checkout.created).astimezone(),
            status=PaymentStatus.pending,
            external_id=checkout.id,
            body=self.converter.unstructure(body),
            data=self.converter.unstructure(data),
        )


class StripeTerminalPaymentMethod:
    """Stripe terminal payment method."""

    def __init__(
        self,
        stripe: StripeClient,
        publishable_key: str,
        converter: Converter,
        reader_id: str,
    ):
        self.stripe = stripe
        self.publishable_key = publishable_key
        self.converter = converter
        self._customer = _StripeCustomerHandler(stripe)
        self.reader_id = reader_id

    async def create_payment(self, request: CreatePaymentRequest) -> PaymentResult:
        """Create a payment."""
        cust_id = await self._customer.get_or_create_customer(request)

        payment_params: PaymentIntentService.CreateParams = {
            "amount": request.pricing_result.total_price,
            "currency": request.pricing_result.currency.lower(),
            "payment_method_types": ["card_present"],
        }

        if cust_id:
            payment_params["customer"] = cust_id

        payment = await self.stripe.payment_intents.create_async(payment_params)

        await self.stripe.terminal.readers.process_payment_intent_async(
            self.reader_id,
            {
                "payment_intent": payment.id,
            },
        )

        body = StripeTerminalPaymentBody(type="terminal")
        data = StripePaymentData(
            type="terminal",
            payment_id=payment.id,
            reader_id=self.reader_id,
        )

        return PaymentResult(
            id=request.id,
            service=request.service,
            date_created=datetime.fromtimestamp(payment.created).astimezone(),
            status=PaymentStatus.pending,
            external_id=payment.id,
            body=self.converter.unstructure(body),
            data=self.converter.unstructure(data),
        )


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
        stripe_config.publishable_key,
        stripe_config.secret_key,
        stripe_config.webhook_secret or "",
        converter,
    )
