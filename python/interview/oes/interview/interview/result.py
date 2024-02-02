"""Result content module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import frozen
from oes.interview.interview.state import InterviewState

if TYPE_CHECKING:
    from oes.interview.interview.step_types.ask import AskResult
    from oes.interview.interview.step_types.exit import ExitResult


@frozen
class StepResult:
    """The result of a step."""

    state: InterviewState
    """The updated :class:`InterviewState`."""

    changed: bool
    """Whether the interview state was changed."""

    content: AskResult | ExitResult | None = None
    """Result content."""
