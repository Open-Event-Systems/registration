"""Access code models."""
from collections.abc import Mapping, Sequence
from typing import Any, Optional
from uuid import UUID

from attrs import frozen


@frozen
class AccessCodeInterview:
    """An interview option from an access code."""

    id: str
    name: str


@frozen
class AccessCodeSettings:
    """Access code settings."""

    registration_id: Optional[UUID] = None
    """Restrict changes to a given registration ID."""

    interviews: Sequence[AccessCodeInterview] = ()
    """The interviews to allow."""

    change_interviews: Sequence[AccessCodeInterview] = ()
    """The change interviews to allow."""

    initial_data: Mapping[str, Any] = {}
    """The data to merge into the interview's initial data."""
