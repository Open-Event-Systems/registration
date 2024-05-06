"""Interview update module."""

from __future__ import annotations

from collections.abc import Mapping
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.immutable import immutable_mapping
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.error import InterviewError
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import AsyncStep, Step
from oes.interview.logic.proxy import make_proxy
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import evaluate
from typing_extensions import TypeIs

if TYPE_CHECKING:
    from oes.interview.interview.interview import Interview

MAX_UPDATE_COUNT = 100


@frozen
class UpdateContext:
    """Interview update context."""

    question_templates: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=immutable_mapping[str, QuestionTemplate]
    )
    state: InterviewState = field(factory=InterviewState)


@frozen
class UpdateResult:
    """The result of an update."""

    state: InterviewState = field(factory=InterviewState)
    content: object | None = None


async def apply_responses(
    state: InterviewState, responses: Mapping[str, Any] | None
) -> InterviewState:
    """Apply user responses."""
    if state.current_question is None or responses is None:
        return state

    changes = state.current_question.parse(responses)
    return _apply_response_values(state, changes)


async def update_interview(interview: Interview, state: InterviewState) -> UpdateResult:
    """Update an interview."""
    updater = _Updater(interview)
    return await updater(state)


def _apply_response_values(
    state: InterviewState, values: Mapping[ValuePointer, Any]
) -> InterviewState:
    cur_data = state.data
    for ptr, value in values.items():
        cur_data = ptr.set(cur_data, value)
    return state.update(data=cur_data, current_question=None)


@frozen
class _Updater:
    interview: Interview

    async def __call__(self, state: InterviewState) -> UpdateResult:
        """Run the interview steps until completed or content is returned."""
        current_state = state
        for _ in range(MAX_UPDATE_COUNT):
            result = await self._run_steps(current_state)
            if result.content is not None or result.state.completed:
                return result
            current_state = result.state
        else:
            raise InterviewError("Max update count exceeded")

    async def _run_steps(self, state: InterviewState) -> UpdateResult:
        """Run through interview steps once."""
        cur_result = UpdateResult(state)
        for step in self.interview.steps:
            proxy_ctx = make_proxy(cur_result.state.template_context)
            if not evaluate(step.when, proxy_ctx):
                continue
            cur_result = await self._run_step(cur_result, step)
            if (
                cur_result.state is not state
                and cur_result.state != state
                or cur_result.content is not None
            ):
                return cur_result
        else:
            updated_state = cur_result.state.update(completed=True)
            return UpdateResult(updated_state)

    async def _run_step(self, prev_result: UpdateResult, step: Step) -> UpdateResult:
        """Run a step and return a result."""
        context = UpdateContext(self.interview, prev_result.state)
        if _is_async_step(step):
            result = await step(context)
        else:
            result = step(context)
        return result


def _is_async_step(step: Step) -> TypeIs[AsyncStep]:
    func = getattr(step, "__call__", step)
    return iscoroutinefunction(func)
