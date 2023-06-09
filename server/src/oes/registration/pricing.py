"""Pricing functions."""
from typing import Any
from uuid import UUID

from oes.registration.models.cart import CartRegistration
from oes.registration.models.event import Event, LineItemRule, ModifierRule
from oes.registration.models.pricing import (
    LineItem,
    Modifier,
    PricingRequest,
    PricingResult,
)


async def default_pricing(
    event: Event,
    request: PricingRequest,
) -> PricingResult:
    """The default pricing function."""
    items = []

    for cart_reg in request.cart.registrations:
        eval_ctx = get_pricing_eval_context(event, cart_reg)
        items.extend(_eval_line_items(cart_reg, event, eval_ctx))

    return PricingResult(
        currency=request.currency,
        line_items=tuple(items),
        total_price=sum(li.total_price for li in items),
    )


def get_pricing_eval_context(
    event: Event, cart_registration: CartRegistration
) -> dict[str, Any]:
    """Get the template context for evaluating pricing conditions."""
    return {
        "event": event,
        "registration": {
            "id": cart_registration.id,
            "old_data": cart_registration.old_data,
            "new_data": cart_registration.new_data,
            "meta": cart_registration.meta or {},
        },
        "added_option_ids": get_added_option_ids(
            cart_registration.old_data, cart_registration.new_data
        ),
    }


def get_added_option_ids(
    old_data: dict[str, Any], new_data: dict[str, Any]
) -> frozenset[str]:
    """Get the set of option_ids added between two registration data."""
    old_ids = old_data.get("option_ids", [])
    new_ids = new_data.get("option_ids", [])

    return frozenset(o for o in new_ids if o not in old_ids)


def _eval_line_items(
    cart_registration: CartRegistration, event: Event, context: dict[str, Any]
):
    for li_rule in event.pricing_rules:
        if li_rule.when_matches(**context):
            yield _make_line_item(cart_registration, li_rule, context)


def _make_line_item(
    cart_registration: CartRegistration, rule: LineItemRule, context: dict[str, Any]
) -> LineItem:
    modifiers = tuple(_eval_modifiers(rule, context))

    return LineItem(
        type_id=rule.type_id,
        registration_id=UUID(cart_registration.new_data.get("id")),
        name=rule.name.render(**context),
        price=rule.price,
        modifiers=modifiers,
        total_price=rule.price + sum(m.amount for m in modifiers),
    )


def _eval_modifiers(li_rule: LineItemRule, context: dict[str, Any]):
    for mod_rule in li_rule.modifiers:
        if mod_rule.when_matches(**context):
            yield _make_modifier(mod_rule, context)


def _make_modifier(rule: ModifierRule, context: dict[str, Any]) -> Modifier:
    return Modifier(
        type_id=rule.type_id.render(**context) if rule.type_id is not None else None,
        name=rule.name.render(**context),
        amount=rule.amount,
    )
