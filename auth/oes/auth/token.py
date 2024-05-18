"""Access token."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Literal

import jwt
import nanoid
from attrs import frozen
from cattrs import BaseValidationError
from cattrs.gen import make_dict_unstructure_fn
from cattrs.preconf.orjson import make_converter
from oes.auth.orm import Base
from sqlalchemy.orm import Mapped, mapped_column
from typing_extensions import Self

converter = make_converter()

DEFAULT_REFRESH_TOKEN_LIFETIME = timedelta(days=3)
GUEST_REFRESH_TOKEN_LIFETIME = timedelta(days=30)
DEFAULT_ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_REUSE_GRACE_PERIOD = timedelta(minutes=1)


class TokenError(ValueError):
    """Raised when a token is invalid."""

    pass


@frozen
class TokenBase:
    """Base token class."""

    iss: Literal["oes"]
    exp: datetime

    def encode(self, *, key: str) -> str:
        """Encode the JWT."""
        as_dict = converter.unstructure(self)
        return jwt.encode(as_dict, key=key, algorithm="HS256")

    @classmethod
    def decode(cls, data: str, *, key: str) -> Self:
        """Decode the JWT."""
        try:
            data = jwt.decode(data, key=key, algorithms=["HS256"], issuer="oes")
        except jwt.InvalidTokenError as exc:
            raise TokenError("Token is invalid") from exc

        try:
            structured = converter.structure(data, cls)
        except BaseValidationError as exc:
            raise TokenError("Token parsing failed") from exc

        return structured


@frozen
class AccessToken(TokenBase):
    """Access token."""

    typ: Literal["at"]
    sub: str | None = None
    email: str | None = None


class RefreshToken(Base, kw_only=True):
    """Refresh token entity."""

    __tablename__ = "refresh_token"

    id: Mapped[str] = mapped_column(
        primary_key=True, default_factory=lambda: RefreshToken._make_id()
    )
    token: Mapped[str] = mapped_column(
        default_factory=lambda: RefreshToken._make_token()
    )
    date_expires: Mapped[datetime]
    date_last_used: Mapped[datetime]
    date_issued: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    num_uses: Mapped[int] = mapped_column(default=1)
    account_id: Mapped[str | None] = mapped_column(default=None)
    email: Mapped[str | None] = mapped_column(default=None)

    def is_valid(self, *, now: datetime | None = None) -> bool:
        """Check that the token is unexpired."""
        now = now if now is not None else datetime.now().astimezone()
        return now < self.date_expires

    def refresh(self, *, exp: datetime | None = None, now: datetime | None = None):
        """Use the refresh token."""
        now = now if now is not None else datetime.now().astimezone()
        self.num_uses += 1
        self.token = self._make_token()
        self.date_last_used = now
        self.date_expires = (
            exp if exp is not None else now + DEFAULT_REFRESH_TOKEN_LIFETIME
        )

    def make_access_token(
        self, *, exp: datetime | None = None, now: datetime | None = None
    ) -> AccessToken:
        """Make an access token from this refresh token."""
        now = now if now is not None else datetime.now().astimezone()
        exp = exp if exp is not None else now + DEFAULT_ACCESS_TOKEN_LIFETIME
        return AccessToken(
            iss="oes",
            typ="at",
            exp=exp,
            sub=self.account_id,
            email=self.email,
        )

    @staticmethod
    def _make_id() -> str:
        return nanoid.generate(_alphabet, 13)

    @staticmethod
    def _make_token() -> str:
        return secrets.token_urlsafe(32)


_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

converter.register_structure_hook(
    datetime, lambda v, t: datetime.fromtimestamp(v).astimezone()
)
converter.register_unstructure_hook(datetime, lambda d: int(d.timestamp()))

converter.register_unstructure_hook_factory(
    lambda cls: isinstance(cls, type) and issubclass(cls, TokenBase),
    lambda cls: make_dict_unstructure_fn(cls, converter, _cattrs_omit_if_default=True),
)
