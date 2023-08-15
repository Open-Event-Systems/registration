import uuid

import pytest
from oes.registration.cart.models import (
    LineItem,
    Modifier,
    PricingError,
    PricingResult,
    PricingResultRegistration,
)


def test_line_item_validation_negative():
    with pytest.raises(PricingError):
        LineItem(
            type_id="item1",
            name="Item 1",
            price=-1,
            total_price=-1,
        )


def test_line_item_validation_total():
    with pytest.raises(PricingError):
        LineItem(
            type_id="item1",
            name="Item 1",
            price=1,
            total_price=2,
        )

    with pytest.raises(PricingError):
        LineItem(
            type_id="item1",
            name="Item 1",
            price=10,
            modifiers=(
                Modifier(
                    type_id="mod1",
                    name="Modifier",
                    amount=-5,
                ),
            ),
            total_price=10,
        )


def test_cart_validation_total():
    id_ = uuid.uuid4()
    with pytest.raises(PricingError):
        PricingResult(
            currency="USD",
            registrations=(
                PricingResultRegistration(
                    registration_id=id_,
                    line_items=(
                        LineItem(
                            type_id="item1",
                            name="Item 1",
                            price=10,
                            modifiers=(
                                Modifier(
                                    type_id="mod1",
                                    name="Modifier",
                                    amount=-5,
                                ),
                            ),
                            total_price=5,
                        ),
                    ),
                ),
            ),
            total_price=10,
        )


def test_line_item_min_0():
    id_ = uuid.uuid4()
    PricingResult(
        currency="USD",
        registrations=(
            PricingResultRegistration(
                registration_id=id_,
                line_items=(
                    LineItem(
                        type_id="item1",
                        name="Item 1",
                        price=10,
                        modifiers=(
                            Modifier(
                                type_id="mod1",
                                name="Modifier",
                                amount=-15,
                            ),
                        ),
                        total_price=0,
                    ),
                ),
            ),
        ),
        total_price=0,
    )


def test_pricing_result_min_0():
    id_ = uuid.uuid4()
    PricingResult(
        currency="USD",
        registrations=(
            PricingResultRegistration(
                registration_id=id_,
                line_items=(
                    LineItem(
                        type_id="item1",
                        name="Item 1",
                        price=10,
                        total_price=10,
                    ),
                ),
            ),
        ),
        modifiers=(
            Modifier(
                type_id="mod2",
                name="Test",
                amount=-15,
            ),
        ),
        total_price=0,
    )


def test_pricing_result():
    id_ = uuid.uuid4()
    PricingResult(
        currency="USD",
        registrations=(
            PricingResultRegistration(
                registration_id=id_,
                line_items=(
                    LineItem(
                        type_id="item1",
                        name="Item 1",
                        price=10,
                        modifiers=(
                            Modifier(
                                type_id="mod1",
                                name="Modifier",
                                amount=-5,
                            ),
                        ),
                        total_price=5,
                    ),
                    LineItem(
                        type_id="item1",
                        name="Item 1",
                        price=10,
                        modifiers=(
                            Modifier(
                                type_id="mod1",
                                name="Modifier",
                                amount=5,
                            ),
                        ),
                        total_price=15,
                    ),
                ),
            ),
        ),
        total_price=20,
    )


def test_pricing_result_no_line_items():
    with pytest.raises(PricingError):
        PricingResult(
            currency="USD",
            registrations=(
                PricingResultRegistration(
                    registration_id=uuid.uuid4(),
                    line_items=(),
                ),
            ),
            total_price=0,
        )


def test_pricing_result_no_registrations():
    with pytest.raises(PricingError):
        PricingResult(
            currency="USD",
            registrations=(),
            total_price=0,
        )
