"""Event stats module."""

from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from oes.registration.orm import Base, Repo
from oes.registration.registration import Registration


class EventStats(Base):
    """Event stats entity."""

    __tablename__ = "event_stats"

    event_id: Mapped[str] = mapped_column(primary_key=True)
    next_number: Mapped[int] = mapped_column(default=1)

    def get_number(self) -> int:
        """Get the next registration number."""
        number = self.next_number
        self.next_number += 1
        return number


class EventStatsRepo(Repo[EventStats, str]):
    """Event stats repository."""

    entity_type = EventStats

    async def get_or_create(self, event_id: str, *, lock: bool = False) -> EventStats:
        """Get or create a :class:`EventStats` row.

        Returns:
            An :class:`EventStats` entity, or ``None`` if a conflict occurred.
        """
        cur = await self.get(event_id, lock=lock)
        if cur:
            return cur
        else:
            entity = EventStats(event_id=event_id)
            self.session.add(entity)
            await self.session.flush()
            return entity


class EventStatsService:
    """Event stats service."""

    def __init__(self, session: AsyncSession, repo: EventStatsRepo):
        self.session = session
        self.repo = repo

    async def get_event_stats(self, event_id: str, *, lock: bool = False) -> EventStats:
        """Get the :class:`EventStats`."""
        return await self.repo.get_or_create(event_id, lock=lock)

    async def assign_numbers(
        self, event_id: str, registrations: Iterable[Registration]
    ):
        """Assign numbers to registrations that do not have one."""
        to_update = tuple(r for r in registrations if r.number is None)
        if not to_update:
            return
        stats = await self.repo.get_or_create(event_id, lock=True)
        for reg in to_update:
            reg.number = stats.get_number()
        await self.session.flush()
