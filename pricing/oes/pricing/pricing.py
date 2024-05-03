"""Pricing module."""

from oes.pricing.config import Config
from oes.pricing.models import PricingRequest
from oes.pricing.script import run_scripts


async def price_cart(config: Config, request: PricingRequest) -> PricingRequest:
    """Price a cart."""
    request = await run_scripts(config.script_dir, request)
    return request
