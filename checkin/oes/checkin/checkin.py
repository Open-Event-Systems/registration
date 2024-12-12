"""Check-in session."""

from collections.abc import Sequence
from datetime import datetime

import nanoid
from oes.checkin.orm import Base
from oes.utils.orm import Repo
from sqlalchemy import Index, String, null, select
from sqlalchemy.orm import Mapped, mapped_column

CHECK_IN_ID_LEN = 14
"""Check-in ID length."""


class CheckIn(Base):
    """Check-in session."""

    __tablename__ = "checkin"
    __table_args__ = (
        Index(
            "ix_checkin_session_id",
            "event_id",
            "session_id",
            unique=True,
        ),
    )

    id: Mapped[str] = mapped_column(String(CHECK_IN_ID_LEN), primary_key=True)
    event_id: Mapped[str]
    session_id: Mapped[str | None] = mapped_column(default=None)
    date_started: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    date_finished: Mapped[datetime | None] = mapped_column(default=None)
    registration_id: Mapped[str | None] = mapped_column(default=None)


class CheckInRepo(Repo[CheckIn, str]):
    """Check-in repo."""

    entity_type = CheckIn

    async def list_active(self, event_id: str) -> Sequence[CheckIn]:
        """List check-ins for an event."""
        q = (
            select(CheckIn)
            .filter(CheckIn.event_id == event_id)
            .filter(CheckIn.date_finished == null())
            .order_by(CheckIn.date_started)
        )
        res = await self.session.execute(q)
        return res.scalars().all()

    async def get_by_session_id(self, event_id: str, session_id: str) -> CheckIn | None:
        """Get a check-in by session ID."""
        q = select(CheckIn).filter(
            CheckIn.event_id == event_id,
            CheckIn.session_id == session_id,
        )
        res = await self.session.execute(q)
        return res.scalar_one_or_none()


class CheckInService:
    """Check-in service."""

    def __init__(self, repo: CheckInRepo):
        self.repo = repo

    def create(
        self, event_id: str, session_id: str | None, registration_id: str | None
    ) -> CheckIn:
        """Create a check-in."""
        check_in = CheckIn(
            id=generate_check_in_id(),
            event_id=event_id,
            session_id=session_id.upper() if session_id else None,
            registration_id=registration_id,
        )
        self.repo.add(check_in)
        return check_in


def generate_check_in_id() -> str:
    """Generate a check-in ID."""
    return nanoid.generate(size=CHECK_IN_ID_LEN)
