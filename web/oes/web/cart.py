"""Cart service."""

from collections.abc import Mapping
from typing import Any

import httpx
from oes.web.config import Config


class CartService:
    """Cart service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def get_cart(self, cart_id: str) -> Mapping[str, Any] | None:
        """Get a cart by id."""
        res = await self.client.get(f"{self.config.cart_service_url}/carts/{cart_id}")
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()

    async def get_pricing_result(self, cart_id: str) -> Mapping[str, Any] | None:
        """Get a cart pricing result."""
        res = await self.client.get(
            f"{self.config.cart_service_url}/carts/{cart_id}/pricing-result"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()

    async def add_to_cart(
        self, cart_id: str, cart_registration: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Add a registration to a cart."""
        body = {"registrations": [cart_registration]}
        res = await self.client.post(
            f"{self.config.cart_service_url}/carts/{cart_id}/registrations", json=body
        )
        res.raise_for_status()
        return res.json()
