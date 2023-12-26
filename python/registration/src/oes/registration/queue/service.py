"""Queue service module."""
from collections.abc import Sequence
from typing import Optional

from oes.registration.queue.entities import QueueItemEntity, StationEntity
from sqlalchemy import null, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load


class QueueService:
    """Queue service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_station(self, id: str, /) -> Optional[StationEntity]:
        """Get a station by ID."""
        return await self.db.get(StationEntity, id)

    async def save_queue_item(self, item: QueueItemEntity, /) -> QueueItemEntity:
        """Save a :class:`QueueItemEntity` to the database."""
        self.db.add(item)
        await self.db.flush()
        return item

    async def get_queue_items(self) -> Sequence[QueueItemEntity]:
        """Get current queue items."""
        q = (
            select(QueueItemEntity)
            .where(QueueItemEntity.date_completed == null())
            .order_by(QueueItemEntity.date_started)
        )
        res = await self.db.execute(q)
        return res.scalars().all()

    async def get_queue_stats(
        self, station_id: Optional[str] = None, /, *, limit: int = 100
    ) -> Sequence[QueueItemEntity]:
        """Get a list of past, successful queue items."""
        q = select(QueueItemEntity).where(
            QueueItemEntity.date_started != null(),
            QueueItemEntity.date_completed != null(),
            QueueItemEntity.success == true(),
        )

        if station_id:
            q = q.where(QueueItemEntity.station_id == station_id)

        q = q.order_by(QueueItemEntity.date_completed.desc())
        q = q.limit(limit)

        q = q.options(
            Load(QueueItemEntity).selectinload(QueueItemEntity.station),
            Load(QueueItemEntity).contains_eager(StationEntity.queue_items),
        )
        q = q.execution_options(populate_existing=True)

        res = await self.db.execute(q)
        return res.scalars().all()
