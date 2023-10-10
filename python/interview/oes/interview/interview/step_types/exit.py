"""Exit step."""
from __future__ import annotations

from typing import Literal, Optional

from attr import frozen
from oes.interview.interview.types import ResultContentType, Step
from oes.interview.interview.update import InterviewUpdate, StepResult
from oes.interview.logic import WhenCondition
from oes.template import Template


@frozen
class ExitStep(Step):
    """Stop the interview."""

    exit: Template
    """The reason."""

    description: Optional[Template] = Template("")
    """An optional description."""

    when: WhenCondition = ()
    """``when`` conditions."""

    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        ctx = update.state.template_context
        return StepResult(
            state=update.state,
            changed=True,
            content=ExitResult(
                title=self.exit.render(ctx),
                description=self.description.render(ctx) if self.description else None,
            ),
        )


@frozen(kw_only=True)
class ExitResult:
    """An exit result."""

    type: Literal[ResultContentType.exit] = ResultContentType.exit
    title: str
    description: Optional[str] = None
