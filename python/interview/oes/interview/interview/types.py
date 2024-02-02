"""Interview types."""
from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from oes.interview.logic.types import Whenable
from typing_extensions import Protocol

if TYPE_CHECKING:
    from oes.interview.interview.result import StepResult
    from oes.interview.interview.update import InterviewUpdate


class ResultContentType(str, Enum):
    """Enum of result content types."""

    question = "question"
    exit = "exit"


class Step(Whenable, Protocol):
    """An interview step."""

    @abstractmethod
    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        """Handle the step.

        Args:
            update: The :class:`InterviewUpdate` object.

        Returns:
            A :class:`StepResult` describing the result.
        """
        ...
