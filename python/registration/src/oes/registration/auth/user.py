"""User module."""
from abc import abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from guardpost import Identity
from oes.registration.auth.scope import Scope, Scopes
from typing_extensions import Protocol


class User(Protocol):
    """User information."""

    @property
    @abstractmethod
    def id(self) -> Optional[UUID]:
        """The user/account ID."""
        ...

    @property
    @abstractmethod
    def email(self) -> Optional[str]:
        """The email."""
        ...

    @property
    @abstractmethod
    def scope(self) -> Scopes:
        """The user's allowed scopes."""
        ...

    @property
    @abstractmethod
    def client_id(self) -> Optional[str]:
        """The client ID."""
        ...

    @property
    @abstractmethod
    def expiration_date(self) -> Optional[datetime]:
        """The expiration date."""
        ...

    def has_scope(self, *scopes: str) -> bool:
        """Return whether the token has all the given scopes."""
        return all(s in self.scope for s in scopes)

    @property
    def is_admin(self) -> bool:
        """Whether the token has the "admin" scope."""
        return self.has_scope(Scope.admin)


class UserIdentity(Identity, User):
    """A :class:`User` implementation."""

    def __init__(
        self,
        id: Optional[UUID] = None,
        email: Optional[str] = None,
        scope: Scopes = Scopes(),
        expiration_date: Optional[datetime] = None,
        client_id: Optional[str] = None,
    ):
        super().__init__(
            {
                "id": id,
                "email": email,
                "scope": scope,
                "expiration_date": expiration_date,
                "client_id": client_id,
            },
            "Bearer",
        )

    @property
    def id(self) -> Optional[UUID]:
        """The user/account ID."""
        return self.claims["id"]

    @property
    def email(self) -> Optional[str]:
        """The email."""
        return self.claims["email"]

    @property
    def scope(self) -> Scopes:
        """The user's allowed scopes."""
        return self.claims["scope"]

    @property
    def client_id(self) -> Optional[str]:
        """The client ID."""
        return self.claims.get("client_id")

    @property
    def expiration_date(self) -> Optional[datetime]:
        """The expiration date."""
        return self.claims.get("expiration_date")
