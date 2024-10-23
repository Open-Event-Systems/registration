"""Type declarations."""

from abc import abstractmethod
from collections.abc import Collection, Iterable, Mapping
from datetime import datetime
from typing import Any, Literal, Protocol, TypeAlias, runtime_checkable

JSON: TypeAlias = Mapping[str, Any]
"""JSON type."""


@runtime_checkable
class Registration(Collection[str], Protocol):
    """Registration object."""

    @abstractmethod
    def __getitem__(self, key: str, /) -> Any: ...

    @abstractmethod
    def keys(self) -> Iterable[str]: ...

    @abstractmethod
    def get(self, key: str, /) -> Any | None: ...

    @property
    @abstractmethod
    def id(self) -> str:
        """The ID."""
        ...

    @property
    @abstractmethod
    def event_id(self) -> str:
        """The event ID."""
        ...

    @property
    @abstractmethod
    def status(self) -> Literal["pending", "created", "canceled"]:
        """The status."""
        ...

    @property
    @abstractmethod
    def version(self) -> int:
        """The version."""
        ...

    @property
    @abstractmethod
    def date_created(self) -> datetime:
        """The date the registration was created."""
        ...

    @property
    @abstractmethod
    def date_updated(self) -> datetime | None:
        """The date the registration was updated."""
        ...

    @abstractmethod
    def has_permission(self, account_id: str | None, email: str | None) -> bool:
        """Get whether a user has permission to view this registration."""
        ...
