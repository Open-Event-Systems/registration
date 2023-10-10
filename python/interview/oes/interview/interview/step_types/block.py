"""Block step."""
from __future__ import annotations

from typing import Sequence

from attr import frozen
from oes.interview.interview.types import Step
from oes.interview.interview.update import InterviewUpdate, StepResult, handle_steps
from oes.interview.logic import WhenCondition


@frozen
class Block(Step):
    """A block of steps."""

    block: Sequence[Step]

    when: WhenCondition = ()
    """``when`` conditions."""

    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        return await handle_steps(update, self.block)
