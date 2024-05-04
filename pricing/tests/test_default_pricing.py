import pytest
from jinja2 import Environment
from oes.pricing.config import Config
from oes.pricing.default_pricing import apply_default_pricing
from oes.pricing.models import (
    Cart,
    CartRegistration,
    LineItem,
    Modifier,
    PricingRequest,
    PricingResult,
    PricingResultRegistration,
)
from oes.utils.logic import (
    ValueOrEvaluable,
    WhenCondition,
    make_value_or_evaluable_structure_fn,
    make_when_condition_structure_fn,
)
from oes.utils.template import Expression, make_expression_structure_fn
from typed_settings.converters import get_default_cattrs_converter


@pytest.mark.asyncio
async def test_default_pricing():
    config_dict = {
        "events": {
            "test": {
                "items": [
                    {
                        "name": "Test",
                        "price": 5000,
                        "when": "new.add",
                        "modifiers": [
                            {"amount": -500, "when": "new.discount is true"},
                            {"amount": 500, "when": "new.addon is true"},
                        ],
                    },
                    {"name": "Skip", "price": 1200, "when": "new.skip"},
                ],
                "modifiers": [{"name": "Cart", "amount": 300, "when": "meta.add_3"}],
            }
        }
    }
    jinja2_env = Environment()
    converter = get_default_cattrs_converter()
    converter.register_structure_hook(
        Expression, make_expression_structure_fn(jinja2_env)
    )
    converter.register_structure_hook(
        ValueOrEvaluable, make_value_or_evaluable_structure_fn(converter)
    )
    converter.register_structure_hook(
        WhenCondition, make_when_condition_structure_fn(converter)
    )
    config = converter.structure(config_dict, Config)

    request = PricingRequest(
        "USD",
        cart=Cart(
            "test",
            [
                CartRegistration(
                    id="reg1",
                    new={
                        "add": True,
                        "discount": True,
                    },
                )
            ],
            meta={
                "add_3": True,
            },
        ),
    )

    result = await apply_default_pricing(config, request)

    expected = PricingResult(
        4800,
        [
            PricingResultRegistration(
                id="reg1",
                name="Registration",
                total_price=4500,
                line_items=[
                    LineItem(
                        name="Test",
                        price=5000,
                        total_price=4500,
                        modifiers=[
                            Modifier(-500),
                        ],
                    )
                ],
            )
        ],
        modifiers=[Modifier(300, name="Cart")],
    )

    assert result == expected
