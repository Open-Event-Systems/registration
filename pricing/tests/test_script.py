import uuid
from pathlib import Path

import pytest
from oes.pricing.config import Config, EventConfig
from oes.pricing.models import (
    Cart,
    CartRegistration,
    LineItem,
    PricingRequest,
    PricingResult,
    PricingResultRegistration,
)
from oes.pricing.script import get_scripts


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

    config = Config({"test": EventConfig(script_dir=Path("tests/scripts/test1"))})

    scripts = await get_scripts(config, request)

    assert len(scripts) == 1
    result = await scripts[0](config, request)

    expected = PricingResult(
        100,
        [PricingResultRegistration(id, 100, [LineItem(100, 100, name="Test")])],
    )

    assert result == expected
