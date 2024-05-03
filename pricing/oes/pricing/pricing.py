"""Pricing module."""

from oes.pricing.config import Config
from oes.pricing.models import FinalPricingResult, PricingRequest
from oes.pricing.script import run_scripts


async def price_cart(config: Config, request: PricingRequest) -> FinalPricingResult:
    """Price a cart."""
    event_config = config.events.get(request.cart.event_id)
    if not event_config:
        raise ValueError(f"No config for event: {request.cart.event_id}")
    results = await run_scripts(event_config.script_dir, request)
    if not results.results:
        raise ValueError("Pricing returned no results")

    last_result = results.results[-1]

    final_result = FinalPricingResult(
        currency=request.currency,
        total_price=last_result.total_price,
        registrations=last_result.registrations,
        modifiers=last_result.modifiers,
    )

    return final_result
