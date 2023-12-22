"""Queue entities."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from oes.registration.entities.base import PKUUID, Base, JSONData
from oes.registration.queue.models import QueueItemData, QueueItemGroup, StationSettings
from oes.registration.serialization import get_converter
from oes.util import get_now
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship


class StationEntity(Base):
    """Station entity."""

    __tablename__ = "queue_station"

    id: str = mapped_column(primary_key=True)
    """The station ID."""

    group: str
    """The group."""

    settings: JSONData
    """Settings data."""

    def get_settings(self) -> StationSettings:
        """Get the station settings."""
        return get_converter().structure(self.settings, StationSettings)

    def set_settings(self, settings: StationSettings, /):
        """Set the station settings."""
        self.settings = get_converter().unstructure(settings)


class QueueItemGroupEntity(Base):
    """Queue item group entity."""

    __tablename__ = "queue_item_group"

    id: PKUUID

    group: str
    """The **configuration** group ID."""

    items: list[QueueItemEntity] = relationship(
        "QueueItemEntity", back_populates="group"
    )


class QueueItemEntity(Base):
    """Queue item entity."""

    __tablename__ = "queue_item"

    id: PKUUID
    queue_item_group_id: str = mapped_column(ForeignKey("queue_item_group.id"))

    complete: bool = mapped_column(default=False, index=True)
    """Whether the entry is complete."""

    success: Optional[bool] = mapped_column(default=None)
    """Whether the check-in was successful."""

    date_created: datetime = mapped_column(default_factory=get_now)
    """The date the item was created."""

    date_complete: Optional[datetime] = mapped_column(default=None)
    """The date the item was completed."""

    data: JSONData
    """Queue item data."""

    group: QueueItemGroupEntity = relationship(
        "QueueItemGroupEntity", back_populates="items"
    )

    def get_data(self) -> QueueItemData:
        """Get the queue item data."""
        return get_converter().structure(self.data, QueueItemData)

    def set_data(self, data: QueueItemData, /):
        """Set the queue item data."""
        self.data = get_converter().unstructure(data)
