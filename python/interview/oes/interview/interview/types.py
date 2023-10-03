"""Interview types."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from oes.interview.input.types import Whenable
from typing_extensions import Protocol

if TYPE_CHECKING:
    from oes.interview.interview.interview import StepResult
    from oes.interview.interview.state import InterviewState


class Step(Whenable, Protocol):
    """A step in an interview."""

    @abstractmethod
    async def __call__(self, state: InterviewState, /) -> StepResult:
        """Handle the step."""
        ...
