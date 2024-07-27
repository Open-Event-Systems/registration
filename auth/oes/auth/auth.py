"""Auth module."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, List, TypeAlias

import nanoid
from oes.auth.orm import Base
from oes.utils.orm import JSONB, Repo
from sqlalchemy import ForeignKey, String, TypeDecorator, func, null, or_
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Self

if TYPE_CHECKING:
    from oes.auth.token import RefreshToken

AUTH_ID_LEN = 14


class Scope(str, Enum):
    """Auth scopes."""

    selfservice = "self-service"
    cart = "cart"
    registration = "registration"
    registration_write = "registration:write"
    admin = "admin"


Scopes: TypeAlias = frozenset[str]


class _ScopesType(TypeDecorator[Scopes]):
    impl = JSONB
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return sorted(value) if value else []

    def process_result_value(self, value, dialect):
        return frozenset(value) if value else frozenset()

    def coerce_compared_value(self, op, value):
        return self.impl_instance.coerce_compared_value(op, value)


class _Unset(Enum):
    unset = 0


_unset = _Unset.unset


class Authorization(Base):
    """Authorization entity."""

    __tablename__ = "auth"

    id: Mapped[str] = mapped_column(String(AUTH_ID_LEN), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(AUTH_ID_LEN))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("auth.id"), default=None)
    name: Mapped[str | None] = mapped_column(default=None)
    email: Mapped[str | None] = mapped_column(default=None)
    date_created: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )

    date_expires: Mapped[datetime | None] = mapped_column(default=None)
    scope: Mapped[Scopes] = mapped_column(_ScopesType, default=frozenset())
    path_length: Mapped[int] = mapped_column(default=0)

    parent: Mapped[Authorization | None] = relationship(
        "Authorization",
        back_populates="children",
        cascade="save-update, merge",
        remote_side=[id],
        default=None,
    )
    children: Mapped[List[Authorization]] = relationship(
        "Authorization",
        back_populates="parent",
        cascade="save-update, merge, delete",
        remote_side=[parent_id],
        default_factory=list,
    )
    refresh_token: Mapped[RefreshToken | None] = relationship(
        "RefreshToken",
        back_populates="authorization",
        cascade="save-update, merge, delete, delete-orphan",
        default=None,
    )

    @hybrid_method
    def get_is_valid(self, *, now: datetime | None = None) -> bool:
        """Return whether the auth is unexpired."""
        now = now or datetime.now().astimezone()
        return self.date_expires is None or now < self.date_expires

    @get_is_valid.inplace.expression
    @classmethod
    def _get_is_valid(cls, *, now: datetime | None = None) -> Any:
        now_val = now if now else func.now()
        return or_(cls.date_expires == null(), cls.date_expires > now_val)

    @hybrid_property
    def can_create_child(self) -> bool:
        """Return whether a child auth may be created."""
        return self.path_length is None or self.path_length > 0

    @can_create_child.inplace.expression
    @classmethod
    def _can_create_child(cls):
        return or_(cls.path_length == null(), cls.path_length > 0)

    def create_child(
        self,
        name: str | None | _Unset = _unset,
        email: str | None | _Unset = _unset,
        date_expires: datetime | None | _Unset = _unset,
        scope: Iterable[str] | _Unset = _unset,
        path_length: int | _Unset = _unset,
    ) -> Self:
        """Create a child authorization."""
        id_ = nanoid.generate(alphabet=_alphabet, size=AUTH_ID_LEN)
        return type(self)(
            id=id_,
            account_id=self.account_id,
            parent_id=self.id,
            name=name if not isinstance(name, _Unset) else self.name,
            email=email if not isinstance(email, _Unset) else self.email,
            date_expires=_combine_expiration(
                (
                    date_expires
                    if not isinstance(date_expires, _Unset)
                    else self.date_expires
                ),
                self.date_expires,
            ),
            scope=frozenset(scope if not isinstance(scope, _Unset) else self.scope)
            & self.scope,
            path_length=_combine_path_len(
                self.path_length,
                (
                    path_length
                    if not isinstance(path_length, _Unset)
                    else self.path_length - 1
                ),
            ),
            parent=self,
        )


def _combine_expiration(d1: datetime | None, d2: datetime | None) -> datetime | None:
    if d1 is None or d2 is None:
        return d1 or d2
    else:
        return min(d1, d2)


def _combine_path_len(p: int, c: int) -> int:
    max_ = p - 1
    return max(min(max_, c), 0)


class AuthRepo(Repo[Authorization, str]):
    """Auth repo."""

    entity_type = Authorization


class AuthService:
    """Auth service."""

    def __init__(self, repo: AuthRepo):
        self.repo = repo

    def create_auth(
        self,
        name: str | None = None,
        email: str | None = None,
        date_created: datetime | None = None,
        date_expires: datetime | None = None,
        scope: Iterable[str] = (),
        path_length: int = 0,
    ) -> Authorization:
        """Create a :class:`Authorization`."""
        id_ = nanoid.generate(alphabet=_alphabet, size=AUTH_ID_LEN)
        date_created = date_created or datetime.now().astimezone()
        return Authorization(
            id=id_,
            account_id=id_,
            name=name,
            email=email,
            date_created=date_created,
            date_expires=date_expires,
            scope=frozenset(scope),
            path_length=path_length,
        )


_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
