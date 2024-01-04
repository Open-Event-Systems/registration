"""Queue entities."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from oes.registration.entities.base import PKUUID, Base, JSONData
from oes.registration.queue.models import QueueItemData, StationSettings
from oes.registration.serialization import get_converter
from oes.util import get_now
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship


class QueueGroupEntity(Base):
    """Queue group entity."""

    __tablename__ = "queue_group"

    id: Mapped[str] = mapped_column(primary_key=True)
    """Group ID."""

    stations: Mapped[list[StationEntity]] = relationship(
        "StationEntity",
        back_populates="group",
        primaryjoin=lambda: foreign(StationEntity.group_id) == QueueGroupEntity.id,
    )


class StationEntity(Base):
    """Station entity."""

    __tablename__ = "queue_station"

    id: Mapped[str] = mapped_column(primary_key=True)
    """The station ID."""

    group_id: Mapped[str]
    """The group ID."""

    settings: Mapped[JSONData]
    """Settings data."""

    queue_items: Mapped[list[QueueItemEntity]] = relationship(
        "QueueItemEntity",
        back_populates="station",
        primaryjoin=lambda: foreign(QueueItemEntity.station_id) == StationEntity.id,
    )

    group: Mapped[Optional[QueueGroupEntity]] = relationship(
        "QueueGroupEntity",
        back_populates="stations",
        primaryjoin=lambda: foreign(StationEntity.group_id) == QueueGroupEntity.id,
    )

    print_requests: Mapped[list[PrintRequestEntity]] = relationship(
        "PrintRequestEntity",
        back_populates="station",
        primaryjoin=lambda: foreign(PrintRequestEntity.station_id) == StationEntity.id,
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

    group_id: Mapped[str]
    """The group ID."""

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
        primaryjoin=lambda: foreign(QueueItemEntity.station_id) == StationEntity.id,
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


class PrintRequestEntity(Base):
    """Print request entity."""

    __tablename__ = "queue_station_print_request"

    id: Mapped[PKUUID]
    """The request ID."""

    station_id: Mapped[str]
    """The station ID."""

    date_created: Mapped[datetime] = mapped_column(
        default=lambda: get_now(), index=True
    )
    """The date the request was created."""

    date_completed: Mapped[Optional[datetime]]
    """The date the request was accepted."""

    data: Mapped[JSONData]
    """Registration data."""

    station: Mapped[StationEntity] = relationship(
        "StationEntity",
        back_populates="print_requests",
        primaryjoin=lambda: foreign(PrintRequestEntity.station_id) == StationEntity.id,
    )
