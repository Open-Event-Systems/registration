"""Pricing result module."""

from collections.abc import Sequence

from attrs import define


@define
class Modifier:
    """Price modifier."""

    amount: int
    name: str | None = None
    id: str | None = None


@define
class LineItem:
    """A line item."""

    price: int
    total_price: int
    modifiers: Sequence[Modifier] = ()

    name: str | None = None
    description: str | None = None
    id: str | None = None


@define
class PricingResultRegistration:
    """A registration."""

    id: str
    total_price: int
    line_items: Sequence[LineItem] = ()

    name: str | None = None


@define
class PricingResult:
    """A pricing result."""

    currency: str
    total_price: int
    registrations: Sequence[PricingResultRegistration] = ()
    modifiers: Sequence[Modifier] = ()
