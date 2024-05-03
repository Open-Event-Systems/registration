"""Type declarations."""

from collections.abc import Callable, Coroutine
from typing import TypeAlias

from oes.pricing.models import PricingRequest, PricingResult

PricingFunction: TypeAlias = Callable[
    [PricingRequest], Coroutine[None, None, PricingResult]
]
