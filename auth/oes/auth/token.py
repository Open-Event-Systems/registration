"""Access token."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Literal

import jwt
from attrs import frozen
from cattrs import BaseValidationError, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from cattrs.preconf.orjson import make_converter
from oes.auth.auth import Authorization, Scopes
from oes.auth.orm import Base
from oes.utils.orm import Repo
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    sub: str
    acc: str | None = None
    email: str | None = None
    scope: Scopes = frozenset()


class RefreshToken(Base, kw_only=True):
    """Refresh token entity."""

    __tablename__ = "refresh_token"

    auth_id: Mapped[str] = mapped_column(ForeignKey("auth.id"), primary_key=True)
    token: Mapped[str] = mapped_column(
        default_factory=lambda: RefreshToken._make_token()
    )
    date_created: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    date_expires: Mapped[datetime]

    authorization: Mapped[Authorization] = relationship(
        "Authorization", back_populates="refresh_token"
    )

    def is_valid(self, *, now: datetime | None = None) -> bool:
        """Check that the token is unexpired."""
        now = now or datetime.now().astimezone()
        return now < self.date_expires and self.authorization.get_is_valid(now=now)

    def make_access_token(
        self, *, exp: datetime | None = None, now: datetime | None = None
    ) -> AccessToken:
        """Make an access token from this refresh token."""
        # TODO: review exp times
        now = now if now is not None else datetime.now().astimezone()
        exp = exp if exp is not None else now + DEFAULT_ACCESS_TOKEN_LIFETIME
        exp = (
            min(exp, self.authorization.date_expires)
            if self.authorization.date_expires
            else exp
        )
        return AccessToken(
            iss="oes",
            typ="at",
            exp=exp,
            sub=self.authorization.id,
            acc=self.authorization.account_id,
            email=self.authorization.email,
            scope=self.authorization.scope,
        )

    @staticmethod
    def _make_token() -> str:
        return secrets.token_urlsafe(32)


class RefreshTokenRepo(Repo[RefreshToken, str]):
    """Refresh token repo."""

    entity_type = RefreshToken


converter.register_structure_hook(
    datetime, lambda v, t: datetime.fromtimestamp(v).astimezone()
)
converter.register_unstructure_hook(datetime, lambda d: int(d.timestamp()))

converter.register_structure_hook(
    AccessToken,
    make_dict_structure_fn(
        AccessToken,
        converter,
        scope=override(struct_hook=lambda v, t: frozenset(v.split())),
    ),
)

converter.register_unstructure_hook(
    AccessToken,
    make_dict_unstructure_fn(
        AccessToken,
        converter,
        _cattrs_omit_if_default=True,
        scope=override(unstruct_hook=lambda v: " ".join(sorted(v))),
    ),
)
