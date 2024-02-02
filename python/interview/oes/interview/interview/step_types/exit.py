"""Exit step."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from attr import frozen
from oes.interview.interview.result import StepResult
from oes.interview.interview.types import ResultContentType
from oes.interview.logic import WhenCondition
from oes.template import Template

if TYPE_CHECKING:
    from oes.interview.interview.update import InterviewUpdate


@frozen
class ExitStep:
    """Stop the interview."""

    exit: Template
    """The reason."""

    description: Template | None = None
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
    description: str | None = None
