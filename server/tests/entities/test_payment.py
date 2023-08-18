import uuid

import pytest
from oes.registration.cart.models import (
    CartData,
    CartRegistration,
    LineItem,
    PricingResult,
    PricingResultRegistration,
)
from oes.registration.checkout.entities import CheckoutEntity, CheckoutState
from oes.registration.util import get_now


def test_properties():
    c = CheckoutEntity(state=CheckoutState.pending)
    assert c.is_open
    assert not c.is_closed

    c = CheckoutEntity(state=CheckoutState.complete)
    assert not c.is_open
    assert c.is_closed

    c = CheckoutEntity(state=CheckoutState.canceled)
    assert not c.is_open
    assert c.is_closed


def test_complete():
    now = get_now()

    c = CheckoutEntity(state=CheckoutState.pending)
    assert c.complete(now)

    assert c.state == CheckoutState.complete
    assert c.date_closed == now

    later = get_now()
    assert not c.complete(later)
    assert c.date_closed == now


def test_cancel():
    now = get_now()

    c = CheckoutEntity(state=CheckoutState.pending)
    assert c.cancel(now)

    assert c.state == CheckoutState.canceled
    assert c.date_closed == now

    later = get_now()
    assert not c.cancel(later)
    assert c.date_closed == now


def test_invalid_state_transition():
    c = CheckoutEntity(state=CheckoutState.canceled)

    with pytest.raises(ValueError):
        c.complete()

    c = CheckoutEntity(state=CheckoutState.complete)

    with pytest.raises(ValueError):
        c.cancel()


def test_set_cart_data():
    id_ = uuid.uuid4()
    cd = CartData(
        event_id="example-event",
        registrations=(
            CartRegistration(
                id=id_,
                old_data={"a": 1},
                new_data={"a": 2},
            ),
        ),
    )

    entity = CheckoutEntity()
    entity.set_cart_data(cd.get_hash(), cd)
    assert entity.cart_id == cd.get_hash()
    assert isinstance(entity.cart_data, dict)
    assert entity.cart_data != {}

    cd2 = entity.get_cart_data()
    assert cd2 == cd


def test_set_pricing_result():
    id_ = uuid.uuid4()
    result = PricingResult(
        currency="USD",
        registrations=(
            PricingResultRegistration(
                registration_id=id_,
                name="Registration",
                line_items=(
                    LineItem(
                        type_id="1",
                        name="Item",
                        price=100,
                        total_price=100,
                    ),
                ),
            ),
        ),
        total_price=100,
    )

    entity = CheckoutEntity()
    entity.set_pricing_result(result)
    assert isinstance(entity.pricing_result, dict)
    assert entity.pricing_result != {}

    result2 = entity.get_pricing_result()
    assert result2 == result
