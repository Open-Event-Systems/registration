import uuid
from pathlib import Path

import pytest
from oes.pricing.models import (
    Cart,
    CartRegistration,
    LineItem,
    PricingRequest,
    PricingResult,
    PricingResultRegistration,
)
from oes.pricing.script import run_scripts


@pytest.mark.asyncio
async def test_run_scripts():
    id = str(uuid.uuid4())
    request = PricingRequest(
        "USD",
        Cart(
            "test",
            [
                CartRegistration(
                    id=id,
                    old={},
                    new={},
                )
            ],
        ),
    )

    result = await run_scripts(Path("tests/scripts/test1"), request)

    expected = PricingRequest(
        "USD",
        Cart(
            "test",
            [
                CartRegistration(
                    id=id,
                    old={},
                    new={},
                )
            ],
        ),
        [
            PricingResult(
                100,
                [PricingResultRegistration(id, 100, [LineItem(100, 100, name="Test")])],
            )
        ],
    )

    assert result == expected
