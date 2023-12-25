"""Queue entities."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from oes.registration.entities.base import PKUUID, Base, JSONData
from oes.registration.queue.models import QueueItemData, StationSettings
from oes.registration.serialization import get_converter
from oes.util import get_now
from sqlalchemy.orm import Mapped, mapped_column, relationship


class StationEntity(Base):
    """Station entity."""

    __tablename__ = "queue_station"

    id: Mapped[str] = mapped_column(primary_key=True)
    """The station ID."""

    group: Mapped[str]
    """The group."""

    settings: Mapped[JSONData]
    """Settings data."""

    queue_items: Mapped[list[QueueItemEntity]] = relationship(
        "QueueItemEntity", back_populates="station"
    )

    def get_settings(self) -> StationSettings:
        """Get the station settings."""
        return get_converter().structure(self.settings, StationSettings)

    def set_settings(self, settings: StationSettings, /):
        """Set the station settings."""
        self.settings = get_converter().unstructure(settings)


class QueueItemEntity(Base):
    """Queue item entity."""

    __tablename__ = "queue_item"

    id: Mapped[PKUUID]

    station_id: Mapped[Optional[str]] = mapped_column(default=None)
    """The assigned station ID."""

    date_created: Mapped[datetime] = mapped_column(default=lambda: get_now())
    """The date the item was created."""

    date_started: Mapped[Optional[datetime]] = mapped_column(default=None)
    """The date service was started."""

    date_completed: Mapped[Optional[datetime]] = mapped_column(default=None, index=True)
    """The date service was completed."""

    success: Mapped[Optional[bool]] = mapped_column(default=None)
    """Whether the check-in was successful."""

    data: Mapped[JSONData]
    """Queue item data."""

    station: Mapped[Optional[StationEntity]] = relationship(
        "StationEntity",
        back_populates="queue_items",
        primaryjoin=lambda: QueueItemEntity.station_id == StationEntity.id,
    )

    def get_data(self) -> QueueItemData:
        """Get the queue item data."""
        return get_converter().structure(self.data, QueueItemData)

    def set_data(self, data: QueueItemData, /):
        """Set the queue item data."""
        self.data = get_converter().unstructure(data)

    @property
    def duration(self) -> float:
        """The duration of the check-in."""
        if not self.date_started or not self.date_completed:
            raise ValueError("Check-in is not complete")
        return (self.date_completed - self.date_started).total_seconds()
