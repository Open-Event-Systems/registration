"""Default pricing logic."""

import itertools
from collections.abc import Iterator

from oes.pricing.config import Config, EventConfig, LineItemConfig, ModifierConfig
from oes.pricing.models import (
    CartRegistration,
    LineItem,
    Modifier,
    PricingRequest,
    PricingResult,
    PricingResultRegistration,
)
from oes.pricing.serialization import converter
from oes.utils.logic import evaluate
from oes.utils.template import TemplateContext


async def apply_default_pricing(
    config: Config, request: PricingRequest
) -> PricingResult:
    """Apply the default pricing logic."""
    event_config = config.events.get(request.cart.event_id)
    if event_config is None:
        raise ValueError(f"No config for event: {request.cart.event_id}")

    ctx = converter.unstructure(request.cart)
    reg_ctx = {r["id"]: r for r in ctx["registrations"]}

    registrations = [
        _handle_registration(event_config, r, reg_ctx[r.id])
        for r in request.cart.registrations
    ]

    modifiers = list(
        itertools.chain.from_iterable(
            _handle_modifier(m, ctx) for m in event_config.modifiers
        )
    )

    total = sum(r.total_price for r in registrations) + sum(m.amount for m in modifiers)

    return PricingResult(
        total_price=total,
        registrations=registrations,
        modifiers=modifiers,
    )


def _handle_registration(
    event_config: EventConfig, registration: CartRegistration, ctx: TemplateContext
) -> PricingResultRegistration:
    line_items = list(
        itertools.chain.from_iterable(
            _handle_line_item(li, ctx) for li in event_config.items
        )
    )
    total = sum(li.total_price for li in line_items)

    return PricingResultRegistration(
        id=registration.id,
        total_price=total,
        line_items=line_items,
        name=_default_get_name(registration),
    )


def _handle_line_item(
    line_item_config: LineItemConfig, ctx: TemplateContext
) -> Iterator[LineItem]:
    if evaluate(line_item_config.when, ctx):
        modifiers = list(
            itertools.chain.from_iterable(
                _handle_modifier(m, ctx) for m in line_item_config.modifiers
            )
        )
        total = line_item_config.price + sum(m.amount for m in modifiers)
        yield LineItem(
            price=line_item_config.price,
            total_price=total,
            modifiers=modifiers,
            name=line_item_config.name,
            description=line_item_config.description,
            id=line_item_config.id,
        )


def _handle_modifier(
    modifier_config: ModifierConfig, ctx: TemplateContext
) -> Iterator[Modifier]:
    if evaluate(modifier_config.when, ctx):
        yield Modifier(
            amount=modifier_config.amount,
            name=modifier_config.name,
            id=modifier_config.id,
        )


def _default_get_name(reg: CartRegistration) -> str:
    fname = reg.new.get("first_name")
    lname = reg.new.get("last_name")
    pname = reg.new.get("preferred_name")

    names = [fname or pname, lname]
    name = " ".join(n for n in names if n)
    return name or "Registration"
