"""Cart module."""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Iterable
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
import orjson
from attrs import define, field
from cattrs.preconf.orjson import make_converter
from oes.cart.config import Config
from oes.cart.orm import Base
from oes.utils.orm import JSON, Repo
from redis.asyncio import Redis
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

CART_PRICING_RESULT_CACHE_TIME = 300
"""Cache time for pricing results, in seconds."""


class CartEntity(Base, kw_only=True):
    """Cart entity."""

    __tablename__ = "cart"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[str]
    date_created: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    cart_data: Mapped[JSON] = mapped_column(default_factory=dict)

    def get_cart(self) -> Cart:
        """Get the :class:`Cart`."""
        return _converter.structure(self.cart_data, Cart)


@define
class CartRegistration:
    """A registration in a cart."""

    id: UUID
    old: JSON = field(factory=dict)
    new: JSON = field(factory=dict)
    meta: JSON = field(factory=dict)


@define
class Cart:
    """Cart object."""

    event_id: str
    meta: JSON = field(factory=dict)
    registrations: list[CartRegistration] = field(factory=list)

    def get_id(self, version: str) -> str:
        """Get the ID for this cart."""
        reg_sorted = Cart(
            self.event_id, self.meta, sorted(self.registrations, key=lambda r: r.id)
        )
        as_dict = _converter.unstructure(reg_sorted)
        data = orjson.dumps(as_dict, option=orjson.OPT_SORT_KEYS)

        h = hashlib.md5(usedforsecurity=False)
        h.update(version.encode())
        h.update(data)
        return base64.urlsafe_b64encode(h.digest()).replace(b"=", b"").decode()


@define
class CartResponse:
    """Cart response body."""

    id: str
    cart: Cart


_converter = make_converter()
_converter.register_structure_hook(UUID, lambda v, t: UUID(v))
_converter.register_unstructure_hook_func(
    lambda cls: isinstance(cls, type) and issubclass(cls, UUID), str
)


def unstructure_cart_entity(v: CartEntity) -> Any:
    """Unstructure a cart entity."""
    cart = v.get_cart()
    cart_data = _converter.unstructure(cart)
    return {"id": v.id, "cart": cart_data}


_converter.register_unstructure_hook(CartEntity, unstructure_cart_entity)


class CartRepo(Repo[CartEntity, str]):
    """Cart repository."""

    entity_type = CartEntity

    async def get(self, id: str, *, lock: bool = False) -> CartEntity | None:
        """Get a cart by ID."""
        cart = await super().get(id, lock=lock)
        return cart


class CartService:
    """Cart service."""

    def __init__(self, repo: CartRepo, version: str):
        self.repo = repo
        self.version = version

    async def add(self, cart: Cart) -> CartEntity:
        """Add a cart to the database."""
        entity = await self._get_or_create(cart)
        return entity

    async def add_to_cart(
        self, cart_entity: CartEntity, registrations: Iterable[CartRegistration]
    ) -> CartEntity:
        """Add registrations to a cart.

        Registrations with the same ID will be replaced.
        """
        cart = cart_entity.get_cart()
        new_by_id = {r.id: r for r in registrations}
        new_list = [new_by_id.pop(cur.id, cur) for cur in cart.registrations]
        new_list.extend(new_by_id.values())
        cart.registrations = new_list

        return await self.add(cart)

    async def remove_from_cart(
        self, cart_entity: CartEntity, registration_id: UUID
    ) -> CartEntity:
        """Remove a registration from a cart.

        Has no effect if the registration is not present.
        """
        cart = cart_entity.get_cart()
        cart.registrations = [r for r in cart.registrations if r.id != registration_id]
        return await self.add(cart)

    async def _get_or_create(self, cart: Cart) -> CartEntity:
        id = cart.get_id(self.version)
        cur = await self.repo.get(id)
        if cur:
            return cur

        data = _converter.unstructure(cart)
        entity = CartEntity(id=id, event_id=cart.event_id, cart_data=data)
        self.repo.add(entity)
        return entity


class CartPricingService:
    """Cart pricing service."""

    def __init__(self, config: Config, client: httpx.AsyncClient, redis: Redis | None):
        self.config = config
        self.client = client
        self.redis = redis

    async def price_cart(self, id: str, cart: Cart) -> bytes:
        """Get a pricing result for a cart."""
        if self.redis:
            cached_bytes = await self.redis.get(f"oes.cart.{id}.pricing-result")
            if cached_bytes:
                return cached_bytes

        data = _converter.unstructure(cart)
        res = await self.client.post(
            f"{self.config.pricing_url}/price-cart",
            json={"currency": self.config.currency, "cart": data},
        )
        res.raise_for_status
        res_bytes = res.content
        if self.redis:
            await self.redis.set(
                f"oes.cart.{id}.pricing-result",
                res_bytes,
                ex=CART_PRICING_RESULT_CACHE_TIME,
            )
        return res_bytes
