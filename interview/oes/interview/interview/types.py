"""Type declarations."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Awaitable
from typing import TYPE_CHECKING, Protocol, TypeAlias, Union

from oes.utils.logic import WhenCondition

if TYPE_CHECKING:
    from oes.interview.interview.interview import InterviewContext
    from oes.interview.interview.update import UpdateResult


class StepBase(Protocol):
    """An interview step."""

    @abstractmethod
    def __call__(
        self, context: InterviewContext, /
    ) -> UpdateResult | Awaitable[UpdateResult]:
        """Update the interview state."""
        ...

    @property
    @abstractmethod
    def when(self) -> WhenCondition:
        """``when`` condition."""
        ...


class SyncStep(StepBase, Protocol):
    """A synchronous interview step."""

    @abstractmethod
    def __call__(self, context: InterviewContext, /) -> UpdateResult:
        """Update the interview state."""
        ...


class AsyncStep(StepBase, Protocol):
    """A synchronous interview step."""

    @abstractmethod
    async def __call__(self, context: InterviewContext, /) -> UpdateResult:
        """Update the interview state."""
        ...


Step: TypeAlias = Union[SyncStep, AsyncStep]
