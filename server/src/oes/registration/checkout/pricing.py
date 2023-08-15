"""Pricing functions."""
import itertools
from typing import Any, Optional
from uuid import UUID

from oes.registration.cart.models import (
    CartRegistration,
    LineItem,
    Modifier,
    PricingRequest,
    PricingResult,
    PricingResultRegistration,
)
from oes.registration.models.event import Event, LineItemRule, ModifierRule
from oes.template import Context


async def default_pricing(
    event: Event,
    request: PricingRequest,
) -> PricingResult:
    """The default pricing function."""
    items = []

    for cart_reg in request.cart.registrations:
        eval_ctx = get_pricing_eval_context(event, cart_reg)
        items.append(_make_pricing_registration(cart_reg, event, eval_ctx))

    return PricingResult(
        currency=request.currency,
        registrations=tuple(items),
        total_price=sum(
            li.total_price
            for li in itertools.chain.from_iterable(cr.line_items for cr in items)
        ),
    )


def get_pricing_eval_context(
    event: Event, cart_registration: CartRegistration
) -> Context:
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


def _make_pricing_registration(
    cart_registration: CartRegistration, event: Event, context: Context
):
    pricing_reg = PricingResultRegistration(
        registration_id=UUID(cart_registration.new_data["id"]),
        line_items=tuple(_eval_line_items(event, context)),
        name=_get_name(cart_registration.new_data),
    )
    return pricing_reg


def _get_name(data: dict[str, Any]) -> Optional[str]:
    # how this is displayed should eventually be customizable
    pname = data.get("preferred_name")
    lname = data.get("last_name")
    fname = data.get("first_name")
    email = data.get("email")

    return pname or (" ".join(n for n in (fname, lname) if n)) or email or None


def _eval_line_items(event: Event, context: Context):
    for li_rule in event.pricing_rules:
        if li_rule.when_matches(**context):
            yield _make_line_item(li_rule, context)


def _make_line_item(rule: LineItemRule, context: Context) -> LineItem:
    modifiers = tuple(_eval_modifiers(rule, context))

    return LineItem(
        type_id=rule.type_id.render(context) if rule.description is not None else None,
        name=rule.name.render(context),
        description=rule.description.render(context)
        if rule.description is not None
        else None,
        price=rule.price,
        modifiers=modifiers,
        total_price=rule.price + sum(m.amount for m in modifiers),
    )


def _eval_modifiers(li_rule: LineItemRule, context: Context):
    for mod_rule in li_rule.modifiers:
        if mod_rule.when_matches(**context):
            yield _make_modifier(mod_rule, context)


def _make_modifier(rule: ModifierRule, context: Context) -> Modifier:
    return Modifier(
        type_id=rule.type_id.render(context) if rule.type_id is not None else None,
        name=rule.name.render(context),
        amount=rule.amount,
    )
