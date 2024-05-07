"""Exit step."""

from typing import Literal

from attrs import frozen
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.update import UpdateResult
from oes.utils.logic import WhenCondition
from oes.utils.template import Template


@frozen(kw_only=True)
class ExitResult:
    """Exit content."""

    type: Literal["exit"] = "exit"
    title: str
    description: str | None = None


@frozen
class ExitStep:
    """Show an error message and stop."""

    exit: Template
    description: Template | None = None
    when: WhenCondition = True

    def __call__(self, context: InterviewContext) -> UpdateResult:
        return UpdateResult(
            context.state,
            ExitResult(
                title=self.exit.render(context.state.template_context),
                description=(
                    self.description.render(context.state.template_context)
                    if self.description
                    else None
                ),
            ),
        )
