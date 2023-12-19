"""Square service."""
import asyncio
import uuid
from asyncio import Semaphore
from collections.abc import Iterable, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Literal, Optional, Union
from uuid import UUID

import orjson
from attrs import Factory, frozen
from cattrs.preconf.orjson import make_converter
from loguru import logger
from oes.registration.cart.models import (
    LineItem,
    Modifier,
    PricingResult,
    PricingResultRegistration,
)
from oes.registration.checkout.entities import CheckoutState
from oes.registration.checkout.models import PaymentServiceCheckout
from oes.registration.payment.errors import (
    CheckoutNotFoundError,
    CheckoutStateError,
    ValidationError,
)
from oes.registration.payment.models import (
    CreateCheckoutRequest,
    UpdateRequest,
    WebhookRequestInfo,
    WebhookResult,
)
from oes.registration.payment.types import (
    CheckoutData,
    CheckoutUpdater,
    PaymentService,
    WebhookHandler,
)
from oes.registration.serialization import get_config_converter, get_converter
from oes.registration.serialization.common import structure_datetime
from square.utilities.webhooks_helper import is_valid_webhook_event_signature

try:
    import square
    from square.client import Client
    from square.http.api_response import ApiResponse
except ImportError:
    square = None

converter = make_converter()


class SquareError(RuntimeError):
    """A Square API error."""

    errors: Sequence[Mapping[str, Any]]

    def __init__(self, errors: Iterable[Mapping[str, Any]] = ()):
        errors_seq = tuple(errors)
        super().__init__(errors_seq)
        self.errors = errors_seq

    def __str__(self) -> str:
        if len(self.errors) > 0:
            err = self.errors[0]
            field = f" (field \"{err['field']}\")" if "field" in err else ""
            return f"{err['category']} {err['code']}: {err['detail']}{field}"
        else:
            return "Square error"


class SquarePaymentMethod(str, Enum):
    """Square payment methods."""

    card = "card"


@frozen(kw_only=True)
class SquarePaymentConfig:
    """Square payment configuration."""

    application_id: str
    """The application ID."""

    access_token: str
    """The application secret key."""

    webhook_signing_key: Optional[str] = None
    """The webhook signing key."""

    location_id: str
    """The location ID."""

    environment: str = "sandbox"
    """The environment type."""

    catalog_item_mapping: Mapping[str, str] = Factory(dict)
    """Map line item type IDs to Square catalog item IDs."""

    modifier_mapping: Mapping[str, str] = Factory(dict)
    """Map modifier type IDs to Square modifier IDs."""


class SquareOrderState(str, Enum):
    """Square order states."""

    open = "OPEN"
    completed = "COMPLETED"
    canceled = "CANCELED"
    # others...


@frozen
class Money:
    """Money structure."""

    amount: int
    currency: str = "USD"


@frozen
class PricingOptions:
    """Order pricing options."""

    auto_apply_discounts: bool = False
    auto_apply_taxes: bool = False


class SquareItemType(str, Enum):
    """Square line item type."""

    item = "ITEM"
    custom = "CUSTOM_AMOUNT"
    # others...


class SquareDiscountType(str, Enum):
    """Square discount type."""

    fixed_percentage = "FIXED_PERCENTAGE"
    fixed_amount = "FIXED_AMOUNT"
    # others...


class SquareDiscountScope(str, Enum):
    """Square discount scope."""

    line_item = "LINE_ITEM"
    order = "ORDER"


@frozen(kw_only=True)
class SquareLineItemModifier:
    """A line item modifier."""

    uid: Optional[str] = None
    catalog_object_id: Optional[str] = None
    name: Optional[str] = None
    quantity: str = "1"
    base_price_money: Money
    total_price_money: Optional[Money] = None
    metadata: Mapping[str, str] = Factory(dict)


@frozen(kw_only=True)
class SquareLineItemDiscount:
    """A discount."""

    uid: Optional[str] = None
    catalog_object_id: Optional[str] = None
    name: Optional[str] = None
    type: str = SquareDiscountType.fixed_amount.value
    percentage: Optional[str] = None
    amount_money: Optional[Money] = None
    applied_money: Optional[Money] = None
    metadata: Mapping[str, str] = Factory(dict)
    scope: str = SquareDiscountScope.line_item.value


@frozen(kw_only=True)
class SquareLineItemAppliedDiscount:
    """An applied discount."""

    uid: Optional[str] = None
    discount_uid: Optional[str] = None
    applied_money: Optional[Money] = None


@frozen(kw_only=True)
class SquareLineItem:
    """A line item in Square."""

    uid: Optional[str] = None
    name: Optional[str] = None
    quantity: str = "1"
    note: Optional[str] = None
    catalog_object_id: Optional[str] = None
    item_type: str = SquareItemType.item.value
    metadata: Mapping[str, str] = Factory(dict)
    modifiers: Sequence[SquareLineItemModifier] = ()
    applied_discounts: Sequence[SquareLineItemAppliedDiscount] = ()
    base_price_money: Money = Money(0)
    total_money: Optional[Money] = None


@frozen(kw_only=True)
class SquareOrder:
    """An order."""

    id: Optional[str] = None
    location_id: str
    state: str
    version: Optional[int] = None
    reference_id: Optional[str] = None
    customer_id: Optional[str] = None
    line_items: Sequence[SquareLineItem] = ()
    discounts: Sequence[SquareLineItemDiscount] = ()
    metadata: Mapping[str, str] = Factory(dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    total_money: Optional[Money] = None
    pricing_options: PricingOptions = PricingOptions()


@frozen(kw_only=True)
class SquareCustomer:
    """A Square customer."""

    id: Optional[str] = None
    version: Optional[int] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email_address: Optional[str] = None


@frozen(kw_only=True)
class SquareOrderUpdatedEventProperties:
    order_id: str
    version: int
    location_id: str
    state: SquareOrderState
    created_at: datetime
    updated_at: datetime


@frozen(kw_only=True)
class SquareOrderUpdatedEventObject:
    order_updated: SquareOrderUpdatedEventProperties


@frozen(kw_only=True)
class SquareOrderUpdatedEventData:
    type: Literal["order_updated"]
    id: str
    object: SquareOrderUpdatedEventObject


@frozen(kw_only=True)
class SquareOrderUpdatedEvent:
    merchant_id: str
    type: Literal["order.updated"]
    event_id: str
    created_at: datetime
    data: SquareOrderUpdatedEventData


@frozen(kw_only=True)
class SquareWebhookEvent:
    type: str


class SquarePaymentService(PaymentService, CheckoutUpdater, WebhookHandler):
    """Square payment service."""

    _sem: ClassVar[Semaphore] = Semaphore(1)  # limit concurrency

    @property
    def id(self) -> str:
        return "square"

    @property
    def name(self) -> str:
        return "Square"

    def __init__(self, config: SquarePaymentConfig):
        self._config = config
        self._client = Client(
            access_token=config.access_token,
            environment=config.environment,
        )

    async def create_checkout(
        self, request: CreateCheckoutRequest, checkout_id: Optional[UUID] = None, /
    ) -> PaymentServiceCheckout:
        order = _make_square_order(
            request.pricing_result,
            self._config.location_id,
            catalog_item_mapping=self._config.catalog_item_mapping,
            modifier_mapping=self._config.modifier_mapping,
            checkout_id=checkout_id,
        )

        async with self._sem:
            created_order: SquareOrder = await asyncio.to_thread(
                self._create_order, order
            )

        assert created_order.id is not None
        assert created_order.total_money is not None

        if created_order.total_money.amount != request.pricing_result.total_price:
            raise ValueError(
                f"Square order {created_order.id} was not created with "
                f"the correct price ({created_order.total_money} != "
                f"{request.pricing_result.total_price} "
                f"{request.pricing_result.currency})"
            )

        email, first_name, last_name = self._get_customer_info(request)

        return PaymentServiceCheckout(
            service=self.id,
            id=created_order.id,
            state=_get_state(created_order.state),
            date_created=created_order.created_at,
            checkout_data={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
            response_data={
                "application_id": self._config.application_id,
                "location_id": self._config.location_id,
                "amount": _format_currency_str(request.pricing_result.total_price),
                "currency": request.pricing_result.currency,
                "sandbox": self._config.environment != "production",
            },
        )

    def get_url(
        self,
        id: str,
        /,
        *,
        checkout_data: Optional[CheckoutData] = None,
    ) -> Optional[str]:
        if checkout_data.get("sandbox") is True:
            base = "https://squareupsandbox.com/dashboard/sales/transactions/"
        else:
            base = "https://squareup.com/dashboard/sales/transactions/"
        return base + id

    async def get_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> Optional[PaymentServiceCheckout]:
        async with self._sem:
            order: Optional[SquareOrder] = await asyncio.to_thread(self._get_order, id)

        if order is None:
            return None

        return PaymentServiceCheckout(
            service=self.id,
            id=id,
            state=_get_state(order.state),
            date_created=order.created_at,
            date_closed=order.closed_at,
        )

    async def cancel_checkout(
        self, id: str, /, *, checkout_data: Optional[CheckoutData] = None
    ) -> PaymentServiceCheckout:
        async with self._sem:
            order: Optional[SquareOrder] = await asyncio.to_thread(self._get_order, id)
            if order is None:
                raise CheckoutNotFoundError

            if order.state == SquareOrderState.canceled:
                return PaymentServiceCheckout(
                    service=self.id,
                    id=id,
                    state=CheckoutState.canceled,
                    date_created=order.created_at,
                    date_closed=order.closed_at,
                )
            elif order.state == SquareOrderState.completed:
                raise CheckoutStateError("Checkout is already complete")

            updated: SquareOrder = await asyncio.to_thread(
                self._update_order_state, order, SquareOrderState.canceled
            )

            return PaymentServiceCheckout(
                service=self.id,
                id=id,
                state=_get_state(updated.state),
                date_created=updated.created_at,
                date_closed=updated.closed_at,
            )

    async def update_checkout(
        self, update_request: UpdateRequest, /
    ) -> PaymentServiceCheckout:
        source_id = update_request.body.get("source_id")
        idempotency_key = update_request.body.get("idempotency_key")
        verification_token = update_request.body.get("verification_token")

        if (
            not source_id
            or not idempotency_key
            or not isinstance(source_id, str)
            or not isinstance(idempotency_key, str)
            or verification_token is not None
            and not isinstance(verification_token, str)
        ):
            raise ValidationError

        order_id = update_request.id

        email = update_request.checkout_data.get("email")

        async with self._sem:
            order: Optional[SquareOrder] = await asyncio.to_thread(
                self._get_order, order_id
            )

            if not order:
                raise CheckoutNotFoundError

            # Create customer
            customer_id = await asyncio.to_thread(
                self._create_customer_on_payment, update_request
            )

            assert order.total_money is not None

            with _transform_errors():
                payment_id: str = await asyncio.to_thread(
                    self._create_payment,
                    order_id=order_id,
                    source_id=source_id,
                    idempotency_key=idempotency_key[:45],
                    amount=order.total_money.amount,
                    currency=order.total_money.currency,
                    customer_id=customer_id,
                    email=email,
                    verification_token=verification_token,
                )

                complete_order: SquareOrder = await asyncio.to_thread(
                    self._pay_order, order_id, payment_id
                )

        return PaymentServiceCheckout(
            service=self.id,
            id=order_id,
            state=_get_state(complete_order.state),
            date_created=order.created_at,
            date_closed=order.closed_at,
        )

    async def handle_webhook(
        self, request_info: WebhookRequestInfo, /
    ) -> WebhookResult:
        if not self._config.webhook_signing_key:
            raise ValidationError

        validated = _validate_webhook(
            request_info, key=self._config.webhook_signing_key
        )
        parsed = _parse_webhook(validated)
        if parsed is None:
            return WebhookResult()

        data = parsed.data.object.order_updated

        return WebhookResult(
            updated_checkout=PaymentServiceCheckout(
                self.id,
                data.order_id,
                _get_state(data.state),
                date_closed=data.updated_at
                if data.state != SquareOrderState.open
                else None,
            )
        )

    def _get_order(self, id: str) -> Optional[SquareOrder]:
        res: ApiResponse = self._client.orders.retrieve_order(id)
        if res.is_success():
            return (
                converter.structure(res.body["order"], SquareOrder)
                if res.body and res.body.get("order")
                else None
            )
        else:
            raise SquareError(res.errors)

    def _get_customer_info(
        self, req: CreateCheckoutRequest
    ) -> Union[tuple[str, Optional[str], Optional[str]], tuple[None, None, None]]:
        """Get the email and name from the cart data.

        Uses the email in the cart.meta.email field, or the first email in the data.
        """
        meta_email = req.cart_data.meta.get("email") if req.cart_data.meta else None

        for reg in req.cart_data.registrations:
            email = reg.new_data.get("email")
            pref_name = reg.new_data.get("preferred_name")
            first_name = reg.new_data.get("first_name")
            last_name = reg.new_data.get("last_name")

            if email and (not meta_email or email.lower() == meta_email.lower()):
                return email, pref_name or first_name, last_name

        return meta_email, None, None

    def _create_order(self, order: SquareOrder) -> SquareOrder:
        res: ApiResponse = self._client.orders.create_order(
            {
                "order": converter.unstructure(order),
            }
        )

        if res.is_success():
            return converter.structure(res.body["order"], SquareOrder)
        else:
            raise SquareError(res.errors)

    def _create_customer_on_payment(
        self,
        request: UpdateRequest,
    ) -> Optional[str]:
        email = request.checkout_data.get("email")
        first_name = request.checkout_data.get("first_name")
        last_name = request.checkout_data.get("last_name")

        try:
            if email:
                customer = self._get_or_create_customer(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                return customer.id
            else:
                return None
        except SquareError:
            # Just ignore errors and continue with payment
            logger.opt(exception=True).error("Failed to get/create Square customer")
            return None

    def _update_order_state(
        self, order: SquareOrder, new_state: SquareOrderState
    ) -> SquareOrder:
        res: ApiResponse = self._client.orders.update_order(
            order.id,
            {
                "order": {
                    "version": order.version,
                    "state": new_state.value,
                },
            },
        )

        if res.is_success():
            return converter.structure(res.body["order"], SquareOrder)
        else:
            raise SquareError(res.errors)

    def _create_payment(
        self,
        order_id: str,
        source_id: str,
        idempotency_key: str,
        amount: int,
        currency: str,
        customer_id: Optional[str] = None,
        email: Optional[str] = None,
        verification_token: Optional[str] = None,
    ) -> str:
        # do not allow users to specify a special source_id
        if source_id in ("CASH", "EXTERNAL"):
            raise ValidationError

        res: ApiResponse = self._client.payments.create_payment(
            {
                "source_id": source_id,
                "idempotency_key": idempotency_key,
                "amount_money": {
                    "amount": amount,
                    "currency": currency,
                },
                "autocomplete": False,
                "order_id": order_id,
                "customer_id": customer_id,
                "location_id": self._config.location_id,
                "verification_token": verification_token,
                "buyer_email_address": email,
            }
        )

        if res.is_success():
            return res.body["payment"]["id"]
        else:
            raise SquareError(res.errors)

    def _pay_order(
        self,
        order_id: str,
        payment_id: str,
    ) -> SquareOrder:
        res: ApiResponse = self._client.orders.pay_order(
            order_id,
            {
                "idempotency_key": str(uuid.uuid4()),
                "payment_ids": [
                    payment_id,
                ],
            },
        )

        if res.is_success():
            return converter.structure(res.body["order"], SquareOrder)
        else:
            raise SquareError(res.errors)

    def _get_or_create_customer(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> SquareCustomer:
        cur = self._search_customer(email)
        if cur:
            return cur
        else:
            new_customer = self._create_customer(email, first_name, last_name)
            return new_customer

    def _search_customer(self, email: str) -> Optional[SquareCustomer]:
        res: ApiResponse = self._client.customers.search_customers(
            {
                "query": {
                    "filter": {
                        "email_address": {
                            "fuzzy": email.lower().strip(),
                        }
                    }
                }
            }
        )

        if res.is_success():
            customers = res.body.get("customers", [])
            if not customers:
                return None
            else:
                return converter.structure(customers[0], SquareCustomer)
        else:
            raise SquareError(res.errors)

    def _create_customer(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> SquareCustomer:
        res: ApiResponse = self._client.customers.create_customer(
            {
                "email_address": email,
                "given_name": first_name,
                "family_name": last_name,
            }
        )

        if res.is_success():
            return converter.structure(res.body["customer"], SquareCustomer)
        else:
            raise SquareError(res.errors)

    def _update_customer(
        self,
        customer: SquareCustomer,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> SquareCustomer:
        new_data: dict[str, Any] = {
            "version": customer.version,
        }

        if first_name is not None:
            new_data["given_name"] = first_name

        if last_name is not None:
            new_data["family_name"] = last_name

        res: ApiResponse = self._client.customers.update_customer(
            customer.id,
            new_data,
        )

        if res.is_success():
            return converter.structure(res.body["customer"], SquareCustomer)
        else:
            raise SquareError(res.errors)


def _get_state(square_state: str) -> CheckoutState:
    if square_state == SquareOrderState.completed:
        return CheckoutState.complete
    elif square_state == SquareOrderState.canceled:
        return CheckoutState.canceled
    else:
        return CheckoutState.pending


def _make_square_order(
    pricing_result: PricingResult,
    location_id: str,
    catalog_item_mapping: Mapping[str, str],
    modifier_mapping: Mapping[str, str],
    checkout_id: Optional[UUID] = None,
    customer_id: Optional[str] = None,
) -> SquareOrder:
    line_items = []
    discounts = []

    for reg in pricing_result.registrations:
        for line_item in reg.line_items:
            square_line_item, line_item_discounts = _make_square_line_item(
                reg,
                line_item,
                currency=pricing_result.currency,
                catalog_item_mapping=catalog_item_mapping,
                modifier_mapping=modifier_mapping,
            )
            line_items.append(square_line_item)
            discounts.extend(line_item_discounts)

    return SquareOrder(
        location_id=location_id,
        state=SquareOrderState.open.value,
        reference_id=str(checkout_id),
        customer_id=customer_id,
        line_items=line_items,
        discounts=discounts,
        pricing_options=PricingOptions(
            auto_apply_discounts=False,
            auto_apply_taxes=False,
        ),
    )


def _make_square_line_item(
    registration: PricingResultRegistration,
    line_item: LineItem,
    currency: str,
    catalog_item_mapping: Mapping[str, str],
    modifier_mapping: Mapping[str, str],
) -> tuple[SquareLineItem, list[SquareLineItemDiscount]]:
    item_uid = str(uuid.uuid4())

    modifiers = [
        _make_square_modifier(m, currency, modifier_mapping)
        for m in line_item.modifiers
        if m.amount >= 0
    ]

    square_discounts = [
        _make_square_discount(m, currency) for m in line_item.modifiers if m.amount < 0
    ]

    discounts = [s[0] for s in square_discounts]
    applied_discounts = [s[1] for s in square_discounts]

    catalog_object_id = (
        catalog_item_mapping.get(line_item.type_id) if line_item.type_id else None
    )

    square_line_item = SquareLineItem(
        uid=item_uid,
        name=line_item.name if not catalog_object_id else None,
        catalog_object_id=catalog_object_id,
        note=registration.name or None,
        base_price_money=Money(
            line_item.price,
            currency=currency,
        ),
        modifiers=modifiers,
        applied_discounts=applied_discounts,
        metadata={
            "registration_id": str(registration.registration_id),
        },
    )

    return square_line_item, list(discounts)


def _make_square_modifier(
    modifier: Modifier,
    currency: str,
    id_mapping: Mapping[str, str],
) -> SquareLineItemModifier:
    catalog_object_id = id_mapping.get(modifier.type_id) if modifier.type_id else None
    return SquareLineItemModifier(
        name=modifier.name if not catalog_object_id else None,
        catalog_object_id=catalog_object_id,
        base_price_money=Money(
            modifier.amount,
            currency=currency,
        ),
    )


def _make_square_discount(
    discount: Modifier,
    currency: str,
) -> tuple[SquareLineItemDiscount, SquareLineItemAppliedDiscount]:
    uid = str(uuid.uuid4())
    applied_uid = str(uuid.uuid4())

    square_discount = SquareLineItemDiscount(
        uid=uid,
        name=discount.name,
        type=SquareDiscountType.fixed_amount.value,
        amount_money=Money(
            -discount.amount,
            currency=currency,
        ),
        applied_money=Money(
            -discount.amount,
            currency=currency,
        ),
    )

    applied = SquareLineItemAppliedDiscount(
        uid=applied_uid,
        discount_uid=uid,
    )

    return square_discount, applied


def _validate_webhook(req: WebhookRequestInfo, *, key: str) -> dict[str, Any]:
    try:
        body_str = req.body.decode()
    except Exception:
        raise ValidationError
    signature = req.headers.get("x-square-hmacsha256-signature")
    if not signature or not is_valid_webhook_event_signature(
        body_str, signature, key, req.url
    ):
        logger.warning("Invalid Square webhook signature")
        raise ValidationError

    return orjson.loads(body_str)


def _parse_webhook(body: Mapping[str, Any]) -> Optional[SquareOrderUpdatedEvent]:
    base = get_converter().structure(body, SquareWebhookEvent)
    if base.type == "order.updated":
        return get_converter().structure(body, SquareOrderUpdatedEvent)
    else:
        logger.warning(f"Unsupported Square webhook: {base.type}")
        return None


def _format_currency_str(amount: int) -> str:
    # TODO: use the correct fractional amount
    whole = amount // 100
    frac = amount % 100
    return f"{whole}.{frac:02}"


@contextmanager
def _transform_errors():
    try:
        yield
    except SquareError as e:
        err = e.errors[0] if e.errors else {}

        if err.get("category") == "PAYMENT_METHOD_ERROR":
            raise ValidationError(_get_error_message(err)) from e

        raise e


_error_messages = {
    "CARD_EXPIRED": "Card is expired",
    "INVALID_CARD": "Invalid card",
    "GENERIC_DECLINE": "Card declined",
    "CVV_FAILURE": "Invalid CVV",
    "INVALID_ACCOUNT": "Invalid card",
    "INSUFFICIENT_FUNDS": "Insufficient funds",
    "TRANSACTION_LIMIT": "Insufficient funds",
    "EXPIRATION_FAILURE": "Card is expired",
    "CARD_DECLINED_VERIFICATION_REQUIRED": "Card declined, verification required",
}


def _get_error_message(err):
    code = err.get("code")
    if code and code in _error_messages:
        return _error_messages[code]
    else:
        return "Payment failed"


converter.register_structure_hook(datetime, lambda v, t: structure_datetime(v))


def create_square_service(
    config_data: Mapping,
) -> Optional[SquarePaymentService]:
    """Factory to create the :class:`SquarePaymentService`."""
    # ensure square is available
    if square is None:
        logger.info("Square library is not installed")
        return None
    config = get_config_converter().structure(config_data, SquarePaymentConfig)
    service = SquarePaymentService(config)
    return service
