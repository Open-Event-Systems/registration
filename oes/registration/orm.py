"""ORM base class."""

from collections.abc import MutableMapping
from datetime import datetime
from typing import Annotated, Any, Generic, TypeAlias, TypeVar

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column

DEFAULT_MAX_STRING_LENGTH = 300
"""Maximum string length."""

JSON: TypeAlias = Annotated[MutableMapping[str, Any], mapped_column(JSONB)]
"""JSON type."""


class Base(MappedAsDataclass, DeclarativeBase):
    """Mapped declarative base."""

    type_annotation_map = {
        datetime: DateTime(timezone=True),
        str: String(DEFAULT_MAX_STRING_LENGTH),
    }


_T = TypeVar("_T")
_E = TypeVar("_E")


class Repo(Generic[_E, _T]):
    """Generic repo class."""

    entity_type: type[_E]

    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, entity: _E):
        """Add an entity to the database."""
        self.session.add(entity)

    async def get(self, id: _T, *, lock: bool = False) -> _E | None:
        """Get an entity by ID."""
        return await self.session.get(self.entity_type, id, with_for_update=lock)

    async def merge(self, entity: _E) -> _E:
        """Update an entity."""
        return await self.session.merge(entity)

    async def delete(self, entity: _E):
        """Delete an entity."""
        await self.session.delete(entity)


def import_entities():
    """Import all entities (used by migrations)."""
    from oes.registration import registration  # noqa
