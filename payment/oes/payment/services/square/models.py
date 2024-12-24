"""Square models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from enum import Enum

from attrs import field, frozen


@frozen
class SquareConfig:
    """Square config."""

    application_id: str
    access_token: str
    sandbox: bool
    location_id: str
    item_map: Mapping[str, str] = field(factory=dict)
    modifier_map: Mapping[str, str] = field(factory=dict)


class Method(str, Enum):
    """Square payment methods."""

    web = "web"
    cash = "cash"


class Environment(str, Enum):
    """Square enviroment."""

    production = "production"
    sandbox = "sandbox"


@frozen
class SquarePaymentData:
    """Square payment data."""

    method: Method
    environment: Environment
    location_id: str
    total_price: int
    total_price_str: str
    currency: str
    email: str | None = None


@frozen
class SquarePaymentBody:
    """Square payment response body."""

    method: Method
    environment: Environment
    application_id: str
    location_id: str
    total_price: int
    total_price_str: str
    currency: str
    change: int | None = None


@frozen
class SquarePaymentUpdateRequestBody:
    """Body sent by client to update a payment."""

    source_id: str
    cash_amount: int | None = None
    verification_token: str | None = None


class OrderState(str, Enum):
    """Order state."""

    open = "OPEN"
    completed = "COMPLETED"
    canceled = "CANCELED"


class OrderLineItemItemType(str, Enum):
    """Order line item item type."""

    item = "ITEM"
    custom_amount = "CUSTOM_AMOUNT"


class OrderLineItemDiscountType(str, Enum):
    """Order line item discount type."""

    fixed_percentage = "FIXED_PERCENTAGE"
    fixed_amount = "FIXED_AMOUNT"
    variable_percentage = "VARIABLE_PERCENTAGE"
    variable_amount = "VARIABLE_AMOUNT"


class OrderLineItemDiscountScope(str, Enum):
    """Order line item discount scope."""

    line_item = "LINE_ITEM"
    order = "ORDER"


class PaymentStatus(str, Enum):
    """Payment status."""

    pending = "PENDING"
    approved = "APPROVED"
    completed = "COMPLETED"
    canceled = "CANCELED"
    failed = "FAILED"


@frozen
class Money:
    """Money."""

    amount: int
    currency: str


@frozen
class PricingOptions:
    """Pricing options."""

    auto_apply_discounts: bool


@frozen(kw_only=True)
class Order:
    """An order."""

    id: str
    location_id: str
    reference_id: str | None = None
    customer_id: str | None = None
    line_items: Sequence[OrderLineItem] = ()
    discounts: Sequence[OrderLineItemDiscount] = ()
    metadata: Mapping[str, str] = field(factory=dict)
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    state: OrderState
    version: int
    total_money: Money
    pricing_options: PricingOptions | None = None


@frozen(kw_only=True)
class CreateOrder:
    """Fields set on order creations."""

    location_id: str
    reference_id: str | None = None
    customer_id: str | None = None
    line_items: Sequence[CreateOrderLineItem] = ()
    discounts: Sequence[CreateOrderLineItemDiscount] = ()
    metadata: Mapping[str, str] | None = None
    pricing_options: PricingOptions | None = None


@frozen(kw_only=True)
class OrderLineItem:
    """Order line item."""

    uid: str | None = None
    name: str | None = None
    quantity: str = "1"
    note: str | None = None
    catalog_object_id: str | None = None
    item_type: OrderLineItemItemType
    metadata: Mapping[str, str] = field(factory=dict)
    modifiers: Sequence[OrderLineItemModifier] = ()
    applied_discounts: Sequence[OrderLineItemAppliedDiscount] = ()
    base_price_money: Money
    total_money: Money


@frozen(kw_only=True)
class CreateOrderLineItem:
    """Fields for order line item creation."""

    uid: str | None = None
    name: str | None = None
    quantity: str = "1"
    note: str | None = None
    catalog_object_id: str | None = None
    item_type: OrderLineItemItemType
    metadata: Mapping[str, str] | None = None
    modifiers: Sequence[CreateOrderLineItemModifier] = ()
    applied_discounts: Sequence[CreateOrderLineItemAppliedDiscount] = ()
    base_price_money: Money | None = None


@frozen(kw_only=True)
class OrderLineItemModifier:
    """Order line item modifier."""

    uid: str | None = None
    catalog_object_id: str | None = None
    name: str | None = None
    quantity: str = "1"
    base_price_money: Money
    total_price_money: Money
    metadata: Mapping[str, str] = field(factory=dict)


@frozen(kw_only=True)
class CreateOrderLineItemModifier:
    """Fields for order line item modifier creation."""

    uid: str | None = None
    catalog_object_id: str | None = None
    name: str | None = None
    quantity: str = "1"
    base_price_money: Money | None = None
    metadata: Mapping[str, str] = field(factory=dict)


@frozen(kw_only=True)
class OrderLineItemDiscount:
    """Order line item discount."""

    uid: str
    catalog_object_id: str | None = None
    name: str | None = None
    type: OrderLineItemDiscountType
    percentage: str | None = None
    amount_money: Money | None = None
    applied_money: Money
    metadata: Mapping[str, str] = field(factory=dict)
    scope: OrderLineItemDiscountScope


@frozen(kw_only=True)
class CreateOrderLineItemDiscount:
    """Fields for order line item discount creation."""

    uid: str | None = None
    catalog_object_id: str | None = None
    name: str | None = None
    type: OrderLineItemDiscountType
    percentage: str | None = None
    amount_money: Money | None = None
    applied_money: Money | None = None
    metadata: Mapping[str, str] | None = None
    scope: OrderLineItemDiscountScope


@frozen(kw_only=True)
class OrderLineItemAppliedDiscount:
    """Order line item applied discount."""

    uid: str | None = None
    discount_uid: str
    applied_money: Money


@frozen(kw_only=True)
class CreateOrderLineItemAppliedDiscount:
    """Fields for order line item applied discount creation."""

    uid: str | None = None
    discount_uid: str


@frozen
class Error:
    """A Square error."""

    category: str
    code: str
    detail: str | None = None
    field: str | None = None


@frozen
class ErrorResponse:
    """Square error response body."""

    status: int
    errors: Sequence[Error]


@frozen
class CreateOrderBody:
    """Create order request body."""

    order: CreateOrder
    idempotency_key: str | None = None


@frozen
class OrderResponseBody:
    """Order response body."""

    order: Order


@frozen
class CustomerResponse:
    """Customer response body."""

    customer: Customer


@frozen
class CustomersResponse:
    """Customers response body."""

    customers: Sequence[Customer] | None = None


@frozen
class Customer:
    """Customer object."""

    id: str
    created_at: datetime
    updated_at: datetime
    updated_at: datetime
    given_name: str | None = None
    family_name: str | None = None
    company_name: str | None = None
    nickname: str | None = None
    email_address: str | None = None


@frozen
class CreateCustomerBody:
    """Fields for customer creation."""

    idempotency_key: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    company_name: str | None = None
    nickname: str | None = None
    email_address: str | None = None


@frozen
class CashPaymentDetails:
    """Cash payment details."""

    buyer_supplied_money: Money
    change_back_money: Money


@frozen
class Payment:
    """Payment object."""

    id: str
    created_at: datetime
    updated_at: datetime
    amount_money: Money
    total_money: Money
    status: PaymentStatus
    cash_details: CashPaymentDetails | None = None


@frozen
class CreateCashPaymentDetails:
    """Fields for cash payment detail creation."""

    buyer_supplied_money: Money


@frozen
class CreatePayment:
    """Create payment body."""

    source_id: str
    idempotency_key: str
    amount_money: Money
    delay_duration: str | None = None
    autocomplete: bool = False
    order_id: str | None = None
    customer_id: str | None = None
    location_id: str | None = None
    verification_token: str | None = None
    buyer_email_address: str | None = None
    cash_details: CreateCashPaymentDetails | None = None


@frozen
class PaymentResponse:
    """Payment response."""

    payment: Payment
