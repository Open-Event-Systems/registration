"""Cart service."""

from collections.abc import Mapping, Sequence
from typing import Any

import httpx
import orjson
from attrs import field, frozen
from cattrs.preconf.orjson import make_converter
from oes.web.config import Config
from oes.web.registration import Registration
from oes.web.types import JSON


@frozen
class CartRegistration:
    """Cart registration object."""

    id: str
    old: Registration
    new: Registration
    meta: JSON = field(factory=dict)


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
        self, cart_id: str, cart_registrations: Sequence[CartRegistration]
    ) -> Mapping[str, Any]:
        """Add a registration to a cart."""
        body = {"registrations": _converter.unstructure(cart_registrations)}
        body_bytes = orjson.dumps(body)
        res = await self.client.post(
            f"{self.config.cart_service_url}/carts/{cart_id}/registrations",
            content=body_bytes,
            headers={"Content-Type": "application/json"},
        )
        res.raise_for_status()
        return res.json()


def make_cart_registration(
    old: Registration | None,
    new: Registration,
    meta: JSON | None,
) -> CartRegistration:
    """Make a cart registration entry."""
    old = old if old is not None else make_placeholder_registration(new)
    return CartRegistration(new.id, old, new, meta or {})


def make_placeholder_registration(reg: Registration) -> Registration:
    """Create a placeholder registration."""
    return Registration(
        {
            "id": reg.id,
            "event_id": reg.event_id,
            "status": "pending",
            "version": 1,
        }
    )


_converter = make_converter()
