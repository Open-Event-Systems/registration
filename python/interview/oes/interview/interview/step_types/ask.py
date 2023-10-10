"""Ask step."""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from attrs import frozen
from oes.interview.input import JSONSchema
from oes.interview.interview import InterviewError, ResultContentType, Step
from oes.interview.logic import WhenCondition

if TYPE_CHECKING:
    from oes.interview.interview.update import InterviewUpdate, StepResult

# prevent circular import
import oes.interview.interview.update


@frozen
class AskStep(Step):
    """Ask a question."""

    ask: str
    """The question ID."""

    when: WhenCondition = ()
    """``when`` conditions."""

    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        # skip if the question was already asked
        if self.ask in update.state.answered_question_ids:
            return oes.interview.interview.update.StepResult(
                update.state, changed=False
            )

        question = update.state.interview.get_question(self.ask)
        if question is None:
            raise InterviewError(f"Question ID not found: {self.ask}")

        schema = question.get_schema(update.state.template_context)

        updated = update.state.set_question(question.id)

        return StepResult(
            state=updated,
            changed=True,
            content=AskResult(schema=schema),
        )


@frozen(kw_only=True)
class AskResult:
    """A result asking a question."""

    type: Literal[ResultContentType.question] = ResultContentType.question
    schema: JSONSchema
