"""Interview models."""
from datetime import datetime
from typing import Any, Optional

from attrs import frozen
from oes.registration.util import get_now


@frozen
class InterviewListItem:
    """An interview list result."""

    id: str
    title: Optional[str]


@frozen
class StartInterviewRequest:
    """Request to start an interview."""

    target_url: str
    submission_id: str
    expiration_date: Optional[datetime] = None
    context: Optional[dict[str, Any]] = None
    data: Optional[dict[str, Any]] = None


@frozen
class InterviewResultRequest:
    """Request the result of an interview."""

    state: str


@frozen
class InterviewResultResponse:
    """The result of an interview."""

    interview: dict[str, Any]
    submission_id: str
    expiration_date: datetime
    complete: bool
    context: dict[str, Any]
    data: dict[str, Any]
    target_url: Optional[str] = None

    def get_valid(
        self, *, target_url: Optional[str] = None, now: Optional[datetime] = None
    ) -> bool:
        """Return whether the result is valid."""
        now = now if now is not None else get_now()

        return (
            self.complete
            and (not target_url or target_url == self.target_url)
            and now < self.expiration_date
        )


@frozen
class InterviewResult:
    """Data from a completed interview."""

    submission_id: str
    interview_id: str
    interview_version: str
    target_url: str
    data: dict[str, Any]
