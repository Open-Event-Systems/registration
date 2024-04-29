"""Cart module."""

from __future__ import annotations

import hashlib
from datetime import datetime
from uuid import UUID

import orjson
from attrs import define, field
from cattrs.preconf.orjson import make_converter
from oes.cart.orm import Base
from oes.utils.orm import JSON, Repo
from sqlalchemy import Column, ForeignKey, String, Table, insert
from sqlalchemy.orm import Mapped, mapped_column, relationship

cart_child_table = Table(
    "cart_child",
    Base.metadata,
    Column("parent_id", ForeignKey("cart.id"), primary_key=True),
    Column("child_id", ForeignKey("cart.id"), primary_key=True),
)


class CartEntity(Base, kw_only=True):
    """Cart entity."""

    __tablename__ = "cart"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[str]
    date_created: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    cart_data: Mapped[JSON] = mapped_column(default_factory=dict)

    parents: Mapped[list[CartEntity]] = relationship(
        "CartEntity",
        cart_child_table,
        primaryjoin=id == cart_child_table.c.child_id,
        secondaryjoin=id == cart_child_table.c.parent_id,
        back_populates="children",
        default_factory=list,
    )
    children: Mapped[list[CartEntity]] = relationship(
        "CartEntity",
        cart_child_table,
        primaryjoin=id == cart_child_table.c.parent_id,
        secondaryjoin=id == cart_child_table.c.child_id,
        back_populates="children",
        default_factory=list,
    )


@define
class CartRegistration:
    """A registration in a cart."""

    id: UUID
    old: JSON
    new: JSON


@define
class Cart:
    """Cart object."""

    event_id: str
    meta: JSON = field(factory=dict)
    registrations: list[JSON] = field(factory=list)

    def get_id(self, salt: bytes, version: str) -> str:
        """Get the ID for this cart."""
        as_dict = _converter.unstructure(self)
        data = orjson.dumps(as_dict, option=orjson.OPT_SORT_KEYS)

        h = hashlib.sha256(usedforsecurity=False)
        h.update(salt)
        h.update(version.encode())
        h.update(data)
        return h.hexdigest()


_converter = make_converter()


class CartRepo(Repo[CartEntity, str]):
    """Cart repository."""

    entity_type = CartEntity

    async def get(
        self, id: str, *, event_id: str | None = None, lock: bool = False
    ) -> CartEntity | None:
        """Get a cart by ID."""
        cart = await super().get(id, lock=lock)
        return (
            None
            if cart is None or event_id is not None and cart.event_id != event_id
            else cart
        )

    async def add_child(self, parent_id: str, child_id: str):
        """Add a parent/child relationship."""
        if parent_id == child_id:
            return
        await self.session.flush()
        q = insert(cart_child_table).values(parent_id=parent_id, child_id=child_id)
        await self.session.execute(q)


class CartService:
    """Cart service."""

    def __init__(self, repo: CartRepo, salt: bytes, version: str):
        self.repo = repo
        self.salt = salt
        self.version = version

    async def add(self, cart: Cart, parent_id: str | None = None) -> CartEntity:
        """Add a cart to the database."""
        if parent_id:
            parent = await self.repo.get(parent_id, event_id=cart.event_id, lock=True)
        else:
            parent = None

        entity = await self._get_or_create(cart)

        if parent:
            await self.repo.add_child(parent.id, entity.id)

        return entity

    async def _get_or_create(self, cart: Cart) -> CartEntity:
        id = cart.get_id(self.salt, self.version)
        cur = await self.repo.get(id, event_id=cart.event_id)
        if cur:
            return cur

        data = _converter.unstructure(cart)
        entity = CartEntity(id=id, event_id=cart.event_id, cart_data=data)
        self.repo.add(entity)
        return entity
