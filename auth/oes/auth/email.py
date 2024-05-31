"""Email auth."""

import secrets
from datetime import datetime, timedelta

from loguru import logger
from oes.auth.mq import MQService
from oes.auth.orm import Base
from oes.utils.orm import Repo, transaction
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing_extensions import Self

MAX_ATTEMPTS = 10
"""Max number of attempts."""

MIN_RESEND_INTERVAL = timedelta(minutes=2)
"""Minimum amount of time between sending emails."""

EXPIRATION_TIME = timedelta(minutes=10)
"""Email expiration time."""

TOKEN_LENGTH = 9
"""Token length."""


class EmailAuth(Base):
    """Email auth entity."""

    __tablename__ = "email_auth"

    email: Mapped[str] = mapped_column(primary_key=True)
    date_sent: Mapped[datetime]
    date_expires: Mapped[datetime]
    attempts: Mapped[int]
    code: Mapped[str] = mapped_column(String(16))

    def can_resend(self, *, now: datetime | None = None) -> bool:
        """Get whether the email can be re-sent."""
        now = now if now is not None else datetime.now().astimezone()
        resend_at = self.date_sent + MIN_RESEND_INTERVAL
        return now >= resend_at

    @property
    def can_attempt(self) -> bool:
        """Whether another attempt can be made."""
        return self.attempts < MAX_ATTEMPTS

    @classmethod
    def create(cls, email: str) -> Self:
        """Create an email auth entity."""
        now = datetime.now().astimezone()
        exp = now + EXPIRATION_TIME
        code = "".join(secrets.choice("0123456789") for _ in range(TOKEN_LENGTH))
        return cls(email.lower(), now, exp, 0, code)


class EmailAuthRepo(Repo[EmailAuth, str]):
    """Email auth repo."""

    entity_type = EmailAuth


class EmailAuthService:
    """Email auth service."""

    def __init__(self, repo: EmailAuthRepo, mq: MQService):
        self.repo = repo
        self.mq = mq

    async def send(self, email: str):
        """Send an email auth code."""
        send = False
        async with transaction():
            entity = await self.repo.get(email.lower(), lock=True)
            if entity is None:
                entity = EmailAuth.create(email)
                self.repo.add(entity)
                send = True
            else:
                if entity.can_attempt and entity.can_resend():
                    entity.attempts += 1
                    entity.date_sent = datetime.now().astimezone()
                    entity.date_expires = entity.date_sent + EXPIRATION_TIME
                    entity.code = "".join(
                        secrets.choice("0123456789") for _ in range(TOKEN_LENGTH)
                    )
                    send = True

        if send:
            await self.mq.publish(
                {
                    "email": email,
                    "code": f"{entity.code[0:3]} {entity.code[3:6]} {entity.code[6:9]}",
                    "date": entity.date_sent.isoformat(),
                }
            )
            logger.debug(f"Email auth code for {email}: {entity.code}")

    async def verify(self, email: str, code: str) -> bool:
        """Verify an email auth code."""
        async with transaction():
            entity = await self.repo.get(email.lower(), lock=True)
            now = datetime.now().astimezone()
            if not entity or not entity.can_attempt or now >= entity.date_expires:
                return False
            elif entity.code == code:
                await self.repo.delete(entity)
                return True
            else:
                entity.attempts += 1
                return False
