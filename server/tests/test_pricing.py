import itertools
import uuid

import pytest
from attrs import evolve
from oes.registration.cart.models import (
    CartData,
    CartRegistration,
    Modifier,
    PricingEventBody,
    PricingRequest,
    PricingResult,
)
from oes.registration.checkout.pricing import default_pricing, get_added_option_ids
from oes.registration.models.event import EventConfig, SimpleEventInfo
from oes.registration.serialization import get_converter


def example_pricing_hook(body: dict):
    """Example pricing hook that adds a 10% discount to every item."""
    body_obj = get_converter().structure(body, PricingEventBody)

    new_result = PricingResult(
        currency=body_obj.request.currency,
        registrations=tuple(
            evolve(
                reg,
                line_items=tuple(
                    evolve(
                        li,
                        modifiers=[
                            *li.modifiers,
                            Modifier(name="10% Discount", amount=-int(li.price * 0.10)),
                        ],
                        total_price=max(0, li.total_price - int(li.price * 0.10)),
                    )
                    for li in reg.line_items
                ),
            )
            for reg in body_obj.prev_result.registrations
        ),
        total_price=max(
            0,
            body_obj.prev_result.total_price
            + sum(
                -int(li.price * 0.10)
                for li in itertools.chain.from_iterable(
                    reg.line_items for reg in body_obj.prev_result.registrations
                )
            ),
        ),
    )
    return get_converter().unstructure(new_result)


def test_get_added_option_ids():
    old_data = {"option_ids": ["a", "b"]}

    new_data = {"option_ids": ["b", "c"]}

    assert get_added_option_ids(old_data, new_data) == {"c"}


@pytest.mark.asyncio
async def test_eval_line_items(example_events: EventConfig):
    id_ = uuid.uuid4()
    event = example_events.get_event("example-event")
    request = PricingRequest(
        currency="USD",
        event=SimpleEventInfo.create(event),
        cart=CartData(
            event_id="example-event",
            registrations=(
                CartRegistration(
                    id=id_,
                    old_data={"id": str(id_), "option_ids": []},
                    new_data={"id": str(id_), "option_ids": ["attendee"]},
                ),
            ),
        ),
    )

    result = await default_pricing(event, request)
    assert result.total_price == 4500
    assert len(result.registrations) == 1
    assert len(result.registrations[0].line_items) == 1
    assert result.registrations[0].line_items[0].price == 5000
    assert result.registrations[0].line_items[0].total_price == 4500
