"""Queue service module."""
from collections.abc import Mapping, Sequence
from datetime import timedelta
from typing import Any, Optional
from uuid import UUID

from oes.registration.queue.entities import (
    PrintRequestEntity,
    QueueGroupEntity,
    QueueItemEntity,
    StationEntity,
)
from oes.registration.queue.models import StationSettings
from oes.util import get_now
from sqlalchemy import null, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load

PRINT_REQUEST_TIMEOUT = timedelta(minutes=5)
"""Time after which a print request will expire."""


class QueueService:
    """Queue service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_group(
        self, id: str, /, *, lock: bool = False
    ) -> Optional[QueueGroupEntity]:
        """Get a :class:`QueueGroupEntity` by ID."""
        return await self.db.get(QueueGroupEntity, id, with_for_update=lock)

    async def ensure_group_exists(self, id: str, /):
        """Ensure the row for a group exists."""
        res = await self.db.get(QueueGroupEntity, id)
        if res is None:
            self.db.add(QueueGroupEntity(id=id))
            await self.db.flush()

    async def get_station(self, id: str, /) -> Optional[StationEntity]:
        """Get a station by ID."""
        return await self.db.get(StationEntity, id)

    async def create_station(
        self,
        id: str,
        /,
        *,
        group_id: str,
        settings: StationSettings,
    ) -> StationEntity:
        """Create a station entity."""
        entity = StationEntity(
            id=id,
            group_id=group_id,
        )
        entity.set_settings(settings)
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def create_print_request(
        self, station_id: str, data: Mapping[str, Any], /
    ) -> PrintRequestEntity:
        """Create a print request."""
        entity = PrintRequestEntity(
            station_id=station_id,
            data=dict(data),
        )
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def get_print_requests(
        self, station_id: str, /
    ) -> Sequence[PrintRequestEntity]:
        """Get pending print requests for a station.

        Returned print requests are removed as a side effect.
        """
        cutoff = get_now() - PRINT_REQUEST_TIMEOUT
        q = (
            select(PrintRequestEntity)
            .where(
                PrintRequestEntity.station_id == station_id,
                PrintRequestEntity.date_created > cutoff,
                PrintRequestEntity.date_completed == null(),
            )
            .order_by(PrintRequestEntity.date_created)
        )
        res = await self.db.execute(q)
        requests = res.scalars().all()
        for req in requests:
            await self.db.delete(req)
        return requests

    async def save_queue_item(self, item: QueueItemEntity, /) -> QueueItemEntity:
        """Save a :class:`QueueItemEntity` to the database."""
        self.db.add(item)
        await self.db.flush()
        return item

    async def get_queue_item(
        self, id: UUID, /, *, lock: bool = False
    ) -> Optional[QueueItemEntity]:
        """Get a queue item by ID."""
        return await self.db.get(QueueItemEntity, id, with_for_update=lock)

    async def get_queue_items(
        self,
        group_id: str,
        /,
        *,
        station_id: Optional[str] = None,
        lock: bool = False,
    ) -> Sequence[QueueItemEntity]:
        """Get current queue items."""
        q = select(QueueItemEntity).where(
            QueueItemEntity.date_completed == null(),
            QueueItemEntity.group_id == group_id,
        )
        if station_id:
            q = q.where(QueueItemEntity.station_id == station_id)
        q = q.order_by(QueueItemEntity.date_started)
        if lock:
            q = q.with_for_update()
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
