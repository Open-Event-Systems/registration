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

    event = "event:view"
    """May view event configuration."""

    self_service = "self-service"
    """May use self-service endpoints and manage one's own registrations."""

    registration = "registration"
    """May search and view registrations."""

    registration_edit = "registration:edit"
    """May edit registrations."""

    registration_action = "registration:action"
    """May use pre-defined registration actions."""

    check_in = "check-in"
    """May check in registrations."""

    queue = "queue"
    """May manage the queue."""

    kiosk = "kiosk"
    """May use kiosk features."""


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
            values = frozenset(s.value if isinstance(s, Scope) else s for s in iterable)

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


DEFAULT_SCOPES = Scopes((Scope.cart, Scope.self_service))
"""The default scopes."""


def get_default_scopes(config: Optional[CommandLineConfig] = None) -> Scopes:
    """Get the default scopes."""
    if config and config.insecure and config.no_auth:
        # for debugging, return all scopes
        return Scopes(v for v in Scope if v != Scope.kiosk)
    else:
        return DEFAULT_SCOPES
