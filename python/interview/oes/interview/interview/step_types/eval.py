"""Eval step."""
from __future__ import annotations

from typing import Sequence

from attr import frozen
from oes.interview.interview.types import Step
from oes.interview.interview.update import InterviewUpdate, StepResult
from oes.interview.logic import WhenCondition
from oes.template import evaluate


@frozen
class EvalStep(Step):
    """Ensure values are present."""

    eval: WhenCondition
    """The expression or expressions to evaluate."""

    when: WhenCondition = ()
    """``when`` conditions."""

    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        ctx = update.state.template_context

        # call __bool__ just to raise an exception for undefined values

        if isinstance(self.eval, Sequence) and not isinstance(self.eval, str):
            for item in self.eval:
                bool(evaluate(item, ctx))
        else:
            bool(evaluate(self.eval, ctx))

        return StepResult(
            state=update.state,
            changed=False,
        )
