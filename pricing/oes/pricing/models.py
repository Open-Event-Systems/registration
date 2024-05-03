"""Pricing models."""

from collections.abc import Mapping, Sequence
from typing import Any

from attrs import define, field


@define
class Modifier:
    """Price modifier."""

    amount: int
    name: str | None = None
    id: str | None = None


def _validate_line_item_total(i, a, v):
    modifier_sum = sum(m.amount for m in i.modifiers)
    expected = i.price + modifier_sum
    if v != expected:
        raise ValueError(f"total_price does not sum: {v} != {expected}")


@define
class LineItem:
    """A line item."""

    price: int
    total_price: int = field(validator=_validate_line_item_total)
    modifiers: Sequence[Modifier] = ()

    name: str | None = None
    description: str | None = None
    id: str | None = None


def _validate_registration_total(i, a, v):
    items_sum = sum(li.total_price for li in i.line_items)
    expected = items_sum
    if v != expected:
        raise ValueError(f"total_price does not sum: {v} != {expected}")


@define
class PricingResultRegistration:
    """A registration."""

    id: str
    total_price: int = field(validator=_validate_registration_total)
    line_items: Sequence[LineItem] = ()

    name: str | None = None


def _validate_total(i, a, v):
    items_sum = sum(r.total_price for r in i.registrations)
    modifier_sum = sum(m.amount for m in i.modifiers)
    expected = items_sum + modifier_sum
    if v != expected:
        raise ValueError(f"total_price does not sum: {v} != {expected}")


@define
class PricingResult:
    """A pricing result."""

    total_price: int = field(validator=_validate_total)
    registrations: Sequence[PricingResultRegistration] = ()
    modifiers: Sequence[Modifier] = ()


@define
class CartRegistration:
    """A registration in a cart."""

    id: str
    old: Mapping[str, Any] = field(factory=dict)
    new: Mapping[str, Any] = field(factory=dict)
    meta: Mapping[str, Any] = field(factory=dict)


@define
class Cart:
    """A cart."""

    event_id: str
    registrations: Sequence[CartRegistration] = ()
    meta: Mapping[str, Any] = field(factory=dict)


@define
class PricingRequest:
    """A cart pricing request."""

    currency: str
    cart: Cart
    results: Sequence[PricingResult] = ()
