"""Auth module."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, List

import nanoid
from oes.auth.orm import Base
from oes.utils.orm import Repo
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from oes.auth.token import RefreshToken
    from oes.auth.webauthn import WebAuthnCredential

AUTH_ID_LEN = 14


class Scope(str, Enum):
    """Auth scopes."""

    selfservice = "self-service"
    cart = "cart"


class Scopes(frozenset[str]):
    """Scopes set."""

    def __new__(cls, val: Iterable[str] = ()) -> Scopes:
        items = val.split() if isinstance(val, str) else val
        return super().__new__(cls, items)

    def __str__(self) -> str:
        """Get a string representation of the scopes."""
        return " ".join(sorted(self))


class Authorization(Base):
    """Authorization entity."""

    __tablename__ = "auth"

    id: Mapped[str] = mapped_column(String(AUTH_ID_LEN), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(AUTH_ID_LEN))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("auth.id"), default=None)
    name: Mapped[str | None] = mapped_column(default=None)
    email: Mapped[str | None] = mapped_column(default=None)
    scope_str: Mapped[str] = mapped_column("scope", default="")
    max_path_length: Mapped[int | None] = mapped_column(default=None)
    date_created: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    date_expires: Mapped[datetime | None] = mapped_column(default=None)

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
    webauthn_credential: Mapped[WebAuthnCredential | None] = relationship(
        "WebAuthnCredential",
        back_populates="authorization",
        cascade="save-update, merge, delete, delete-orphan",
        default=None,
    )

    @property
    def scope(self) -> Scopes:
        """The scopes."""
        return Scopes(self.scope_str)

    @scope.setter
    def scope(self, value: Iterable[str]):
        """Set the scopes."""
        self.scope_str = str(Scopes(value))

    def is_valid(self, *, now: datetime | None = None) -> bool:
        """Return whether the auth is expired."""
        now = now or datetime.now().astimezone()
        return self.date_expires is None or now < self.date_expires

    @property
    def can_create_child(self) -> bool:
        """Return whether a child auth may be created."""
        return self.max_path_length is None or self.max_path_length > 0


class AuthRepo(Repo[Authorization, str]):
    """Auth repo."""

    entity_type = Authorization


_unset: Any = object()


class AuthService:
    """Auth service."""

    def __init__(self, repo: AuthRepo):
        self.repo = repo

    def create_auth(
        self,
        *,
        parent: Authorization | None = None,
        account_id: str | None = None,
        name: str | None = None,
        email: str | None = _unset,
        scope: Scopes = Scopes(),
        date_expires: datetime | None = None,
        max_path_length: int | None = 0,
    ) -> Authorization:
        """Create a :class:`Authorization`."""
        id_ = nanoid.generate(alphabet=_alphabet, size=AUTH_ID_LEN)
        auth = Authorization(
            id=id_,
            account_id=(
                account_id if account_id else parent.account_id if parent else id_
            ),
            name=name,
            email=email if email is not _unset else parent.email if parent else None,
            date_expires=_merge_expires(
                parent.date_expires if parent else None, date_expires
            ),
            max_path_length=(
                max_path_length
                if parent is None
                else _get_child_max_path_len(parent.max_path_length)
            ),
            parent=parent,
        )
        auth.scope = _merge_scopes(parent.scope, scope) if parent else scope
        self.repo.add(auth)
        return auth


def _merge_expires(a: datetime | None, b: datetime | None):
    if not a or not b:
        return a or b
    return min(a, b)


def _merge_scopes(a: Scopes, b: Scopes) -> Scopes:
    return Scopes(a & b)


def _get_child_max_path_len(parent_len: int | None) -> int | None:
    if parent_len is None:
        return None
    else:
        return max(0, parent_len - 1)


_alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
