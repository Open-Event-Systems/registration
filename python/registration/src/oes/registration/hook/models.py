"""Hook models."""
from __future__ import annotations

from collections.abc import Generator, Iterable, Mapping, Sequence
from enum import Enum

from attrs import Factory, field, frozen

RETRY_SECONDS = (
    5,
    30,
    60,
    600,
    3600,
    7200,
    43200,
    86400,
)
"""How many seconds between each retry."""

NUM_RETRIES = len(RETRY_SECONDS)
"""Number of attempts to re-send a hook."""


class HookEvent(str, Enum):
    """Hook event types."""

    email_auth_code = "email.auth_code"
    """An email auth code is generated."""

    registration_pending = "registration.pending"
    """A registration is created in the ``pending`` state."""

    registration_created = "registration.created"
    """A registration is created or transitions to the ``created`` state."""

    registration_updated = "registration.updated"
    """A registration is updated without changing its state."""

    registration_canceled = "registration.canceled"
    """A registration is canceled."""

    cart_price = "cart.price"
    """A cart is being priced."""

    checkout_created = "checkout.created"
    """A checkout is created."""

    checkout_closed = "checkout.completed"
    """A checkout is completed."""

    checkout_canceled = "checkout.canceled"
    """A checkout is canceled."""


@frozen
class HookConfigEntry:
    """Hook configuration entry."""

    on: HookEvent
    """The hook trigger."""

    url: str = field(repr=False)
    """The hook URL."""

    retry: bool = True
    """Whether to retry the hook if it fails."""


@frozen
class HookConfig:
    """Hook configuration."""

    hooks: Sequence[HookConfigEntry]
    _by_event: Mapping[str, list[HookConfigEntry]] = field(
        init=False,
        eq=False,
        default=Factory(lambda s: _build_by_event(s.hooks), takes_self=True),
    )

    def __iter__(self) -> Generator[HookConfigEntry, None, None]:
        yield from self.hooks

    def get_by_event(
        self, hook_event: HookEvent
    ) -> Generator[HookConfigEntry, None, None]:
        """Yield :class:`HookConfigEntry` objects for the given event type."""
        yield from self._by_event.get(hook_event, [])


def _build_by_event(
    hooks: Iterable[HookConfigEntry],
) -> dict[str, list[HookConfigEntry]]:
    dict_: dict[str, list[HookConfigEntry]] = {}
    for obj in hooks:
        list_ = dict_.setdefault(obj.on, [])
        list_.append(obj)
    return dict_
