"""Access code models."""
from collections.abc import Mapping, Set
from typing import Any, Optional
from uuid import UUID

from attrs import frozen


@frozen
class AccessCodeSettings:
    """Access code settings."""

    registration_id: Optional[UUID] = None
    """Restrict changes to a given registration ID."""

    interview_ids: Set[str] = frozenset()
    """The interview IDs to allow."""

    change_interview_ids: Set[str] = frozenset()
    """The change interview IDs to allow."""

    initial_data: Mapping[str, Any] = {}
    """The data to merge into the interview's initial data."""
