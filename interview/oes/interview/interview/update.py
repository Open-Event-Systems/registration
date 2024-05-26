"""Interview update module."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any

from attrs import evolve, field, frozen
from oes.interview.interview.error import InterviewError
from oes.interview.interview.resolve import resolve_undefined_values
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import AsyncStep, Step
from oes.interview.logic.proxy import make_proxy
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import evaluate
from typing_extensions import TypeIs

if TYPE_CHECKING:
    from oes.interview.interview.interview import InterviewContext

MAX_UPDATE_COUNT = 100


@frozen
class UpdateResult:
    """The result of an update."""

    state: InterviewState = field(factory=InterviewState)
    content: object | None = None


async def update_interview(
    interview_context: InterviewContext, responses: Mapping[str, Any] | None = None
) -> tuple[InterviewContext, object | None]:
    """Update an interview."""
    # apply responses first
    if interview_context.state.current_question is not None:
        if responses is None:
            # probably needs to be moved
            from oes.interview.interview.step_types.ask import AskResult

            # if no responses were provided, return the same state unchanged
            return interview_context, AskResult(
                schema=interview_context.state.current_question.get_question(
                    interview_context.state.template_context
                ).schema
            )
        state = apply_responses(interview_context.state, responses or {})
        interview_context = evolve(interview_context, state=state)
    return await run_steps(interview_context, interview_context.steps)


def apply_responses(
    state: InterviewState, responses: Mapping[str, Any]
) -> InterviewState:
    """Apply user responses."""
    if state.current_question is None:
        return state

    question = state.current_question.get_question(state.template_context)
    changes = question.parse(responses)
    return _apply_response_values(state, changes)


def _apply_response_values(
    state: InterviewState, values: Mapping[ValuePointer, Any]
) -> InterviewState:
    cur_data = state.data
    for ptr, value in values.items():
        cur_data = ptr.set(cur_data, value)
    return state.update(data=cur_data, current_question=None)


async def run_steps(
    interview_context: InterviewContext, steps: Sequence[Step]
) -> tuple[InterviewContext, object | None]:
    """Run the interview steps until completed or content is returned."""
    updater = _Updater(interview_context)
    result = await updater(steps)
    final_context = evolve(interview_context, state=result.state)
    return final_context, result.content


@frozen
class _Updater:
    initial_context: InterviewContext

    async def __call__(self, steps: Sequence[Step]) -> UpdateResult:
        """Run the interview steps until completed or content is returned."""
        current_state = self.initial_context.state
        for _ in range(MAX_UPDATE_COUNT):
            result = await self._run_steps(current_state, steps)
            if result.content is not None or result.state.completed:
                return result
            current_state = result.state
        else:
            raise InterviewError("Max update count exceeded")

    async def _run_steps(
        self, state: InterviewState, steps: Sequence[Step]
    ) -> UpdateResult:
        """Run through interview steps once."""
        # probably needs to be moved
        from oes.interview.interview.step_types.ask import AskResult

        cur_result = UpdateResult(state)
        with resolve_undefined_values(self.initial_context) as resolver:
            for step in steps:
                proxy_ctx = make_proxy(cur_result.state.template_context)
                if not evaluate(step.when, proxy_ctx):
                    continue
                cur_result = await self._run_step(cur_result, step)
                if (
                    cur_result.content is not None
                    or cur_result.state is not state
                    and cur_result.state != state
                ):
                    return cur_result
            else:
                updated_state = cur_result.state.update(completed=True)
                return UpdateResult(updated_state)

        # if we got here, we have an undefined value to ask about
        question_id, question_template, question = resolver.result
        state = cur_result.state.update(
            answered_question_ids=cur_result.state.answered_question_ids
            | {question_id},
            current_question=question_template,
        )
        result = UpdateResult(state, AskResult(schema=question.schema))
        return result

    async def _run_step(self, prev_result: UpdateResult, step: Step) -> UpdateResult:
        """Run a step and return a result."""
        base_context = evolve(self.initial_context, state=prev_result.state)
        if _is_async_step(step):
            result = await step(base_context)
        else:
            result = step(base_context)
        return result


def _is_async_step(step: Step) -> TypeIs[AsyncStep]:
    func = getattr(step, "__call__", step)
    return iscoroutinefunction(func)
