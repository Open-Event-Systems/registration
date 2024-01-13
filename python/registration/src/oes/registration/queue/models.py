"""Queue models."""
from collections.abc import Mapping, Sequence, Set
from typing import Optional

from attrs import field, frozen
from oes.registration.models.registration import Registration


@frozen
class StationSettings:
    """Station settings object."""

    open: bool = False
    max_queue_length: int = 1
    tags: Set[str] = frozenset()
    delegate_printing_station: Optional[str] = None
    auto_print_url: Optional[str] = None
    feature_intercept: float = 1.0
    feature_coefficients: Mapping[str, float] = {}


@frozen
class QueueItemData:
    """Queue item data."""

    priority: int = 1
    tags: Set[str] = frozenset()
    features: Mapping[str, float] = field(factory=dict)
    scan_data: Optional[str] = None
    registration: Optional[Registration] = None
    duration: Optional[float] = None


@frozen
class QueueItemGroupData:
    """Queue item group data."""

    items: Sequence[QueueItemData] = ()
