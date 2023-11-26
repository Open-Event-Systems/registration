"""Scope module."""
from collections.abc import Set
from enum import Enum
from typing import Iterable, Iterator, Optional

from attrs import frozen
from oes.registration.config import CommandLineConfig


class Scope(str, Enum):
    """Authorization scopes."""

    admin = "admin"
    """May use administration endpoints."""

    cart = "cart"
    """May use cart endpoints."""

    checkout = "checkout"
    """May search and view checkouts."""

    event = "event"
    """May use event endpoints."""

    self_service = "self-service"
    """May use self-service endpoints and manage one's own registrations."""

    registration = "registration"
    """May search and view registrations."""

    registration_edit = "registration:edit"
    """May edit registrations."""


@frozen(init=False, repr=False, order=False)
class Scopes(Set[str]):
    """A set of scopes."""

    _set: frozenset[str]

    def __init__(self, iterable: Iterable[str] = ()):
        if isinstance(iterable, Scopes):
            values = iterable._set
        elif isinstance(iterable, str):
            values = frozenset(iterable.split())
        else:
            values = frozenset(iterable)

        object.__setattr__(self, "_set", values)

    def __contains__(self, x: object) -> bool:
        return x in self._set

    def __len__(self) -> int:
        return len(self._set)

    def __iter__(self) -> Iterator[str]:
        return iter(self._set)

    def __str__(self) -> str:
        return " ".join(sorted(self))

    def __repr__(self) -> str:
        strs = ", ".join(repr(s) for s in sorted(self))
        return f"{{{strs}}}"


# TODO: remove event scope
DEFAULT_SCOPES = Scopes((Scope.event, Scope.cart, Scope.self_service))
"""The default scopes."""


def get_default_scopes(config: Optional[CommandLineConfig] = None) -> Scopes:
    """Get the default scopes."""
    if config and config.insecure and config.no_auth:
        # for debugging, return all scopes
        return Scopes(Scope.__members__.values())
    else:
        return DEFAULT_SCOPES
