import json
import os
import uuid

import pytest
import pytest_asyncio
from oes.registration.cart.models import (
    CartData,
    CartRegistration,
    LineItem,
    Modifier,
    PricingResult,
    PricingResultRegistration,
)
from oes.registration.payment.base import CreateCheckoutRequest, PaymentService
from oes.registration.payment.services.stripe import StripeConfig, StripePaymentService
from oes.registration.payment.square import SquareConfig, SquarePaymentService


def make_stripe_service():
    secret_key = os.getenv("TEST_STRIPE_SECRET_KEY")
    if not secret_key:
        pytest.skip("TEST_STRIPE_SECRET_KEY not set")

    try:
        import stripe  # noqa
    except ImportError:
        pytest.skip("stripe library not installed")

    return StripePaymentService(
        StripeConfig(
            "",
            secret_key,
        )
    )


def make_square_service():
    access_token = os.getenv("TEST_SQUARE_ACCESS_TOKEN")
    location_id = os.getenv("TEST_SQUARE_LOCATION_ID")
    catalog_item_mapping_str = os.getenv("TEST_SQUARE_CATALOG_ITEM_MAPPING")
    modifier_mapping_str = os.getenv("TEST_SQUARE_MODIFIER_MAPPING")

    if not access_token:
        pytest.skip("TEST_SQUARE_ACCESS_TOKEN not set")

    if not location_id:
        pytest.skip("TEST_SQUARE_LOCATION_ID not set")

    catalog_item_mapping = (
        json.loads(catalog_item_mapping_str) if catalog_item_mapping_str else {}
    )
    modifier_mapping = json.loads(modifier_mapping_str) if modifier_mapping_str else {}

    try:
        import square  # noqa
    except ImportError:
        pytest.skip("squareup library not installed")

    return SquarePaymentService(
        SquareConfig(
            application_id="changeit",
            access_token=access_token,
            location_id=location_id,
            environment="sandbox",
            catalog_item_mapping=catalog_item_mapping,
            modifier_mapping=modifier_mapping,
        )
    )


@pytest.fixture(
    params=[
        # make_stripe_service,
        make_square_service
    ]
)
def payment_service(request):
    service = request.param()
    return service


@pytest.fixture
def checkout_request(payment_service: PaymentService):
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    req = CreateCheckoutRequest(
        service=payment_service.id,
        cart_data=CartData(
            event_id="example-event",
            registrations=(
                CartRegistration(
                    id=id1,
                    old_data={},
                    new_data={},
                ),
                CartRegistration(
                    id=id2,
                    old_data={},
                    new_data={},
                ),
            ),
        ),
        pricing_result=PricingResult(
            currency="USD",
            registrations=(
                PricingResultRegistration(
                    registration_id=id1,
                    name="Test Registration 1",
                    line_items=(
                        LineItem(
                            type_id="item1",
                            name="Test Item 1",
                            modifiers=(
                                Modifier(
                                    type_id="modifier1", name="Addon 1", amount=1500
                                ),
                                Modifier(
                                    type_id="discount1", name="Discount 1", amount=-500
                                ),
                            ),
                            price=5000,
                            total_price=6000,
                        ),
                    ),
                ),
                PricingResultRegistration(
                    registration_id=id2,
                    name="Test Registration 2",
                    line_items=(
                        LineItem(
                            type_id="item1",
                            name="Test Item 1",
                            modifiers=(
                                Modifier(
                                    type_id="modifier1", name="Addon 1", amount=1500
                                ),
                                Modifier(
                                    type_id="discount1", name="Discount 1", amount=-500
                                ),
                            ),
                            price=5000,
                            total_price=6000,
                        ),
                        LineItem(
                            type_id="item2",
                            name="Test Item 2",
                            modifiers=(
                                Modifier(
                                    type_id="discount1", name="Discount 1", amount=-500
                                ),
                                Modifier(
                                    type_id="discount2", name="Discount 2", amount=-500
                                ),
                            ),
                            price=1000,
                            total_price=0,
                        ),
                    ),
                ),
            ),
            total_price=12000,
        ),
    )

    return req


@pytest_asyncio.fixture
async def created_checkout_request(
    checkout_request: CreateCheckoutRequest, payment_service: PaymentService
):
    return await payment_service.create_checkout(checkout_request)
