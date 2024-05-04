"""Pricing module."""

from collections.abc import Callable, Coroutine

from oes.pricing.config import Config
from oes.pricing.default_pricing import apply_default_pricing
from oes.pricing.models import FinalPricingResult, PricingRequest, PricingResult
from oes.pricing.script import get_scripts


async def price_cart(config: Config, request: PricingRequest) -> FinalPricingResult:
    """Price a cart."""
    fns: list[
        Callable[[Config, PricingRequest], Coroutine[None, None, PricingResult]]
    ] = [apply_default_pricing]
    fns.extend(await get_scripts(config, request))

    cur_request = request
    for fn in fns:
        result = await fn(config, cur_request)
        cur_request = _update_request(cur_request, result)

    last_result = cur_request.results[-1]

    final_result = FinalPricingResult(
        currency=request.currency,
        total_price=last_result.total_price,
        registrations=last_result.registrations,
        modifiers=last_result.modifiers,
    )

    return final_result


def _update_request(prev: PricingRequest, result: PricingResult) -> PricingRequest:
    return PricingRequest(
        currency=prev.currency, cart=prev.cart, results=(*prev.results, result)
    )
