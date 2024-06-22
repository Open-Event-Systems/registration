"""Interview update module."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from inspect import iscoroutinefunction
from typing import Any

from attrs import evolve, field, frozen
from oes.interview.interview.error import InterviewError
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.resolve import resolve_undefined_values
from oes.interview.interview.state import InterviewState, ParentInterviewContext
from oes.interview.interview.types import AsyncStep, Step
from oes.interview.logic.proxy import make_proxy
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import evaluate
from typing_extensions import TypeIs

MAX_UPDATE_COUNT = 100


@frozen
class UpdateResult:
    """The result of an update."""

    context: InterviewContext = field(factory=InterviewContext)
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
    return await run_steps(interview_context)


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
    interview_context: InterviewContext,
) -> tuple[InterviewContext, object | None]:
    """Run the interview steps until completed or content is returned."""
    updater = _Updater(interview_context)
    result = await updater()
    return result.context, result.content


@frozen
class _Updater:
    initial_context: InterviewContext

    async def __call__(self) -> UpdateResult:
        """Run the interview steps until completed or content is returned."""
        current_context = self.initial_context
        for _ in range(MAX_UPDATE_COUNT):
            result = await self._run_steps(current_context, current_context.steps)
            if result.content is not None or result.context.state.completed:
                return result
            current_context = result.context
        else:
            raise InterviewError("Max update count exceeded")

    async def _run_steps(
        self, context: InterviewContext, steps: Sequence[Step]
    ) -> UpdateResult:
        """Run through interview steps once."""
        # probably needs to be moved
        from oes.interview.interview.step_types.ask import AskResult

        cur_result = UpdateResult(context)
        proxy_ctx = make_proxy(cur_result.context.state.template_context)
        with resolve_undefined_values(context) as resolver:
            for step in steps:
                if not evaluate(step.when, proxy_ctx):
                    continue
                next_result = await self._run_step(cur_result, step)
                if (
                    next_result.content is not None
                    or next_result.context.state is not cur_result.context.state
                    and next_result.context.state != cur_result.context.state
                ):
                    return next_result
                cur_result = next_result
            else:
                return self._handle_complete(cur_result.context)

        # if we got here, we have an undefined value to ask about
        question_id, question_template, question = resolver.result
        state = cur_result.context.state.update(
            answered_question_ids=cur_result.context.state.answered_question_ids
            | {question_id},
            current_question=question_template,
        )
        result = UpdateResult(
            cur_result.context.with_state(state), AskResult(schema=question.schema)
        )
        return result

    async def _run_step(self, prev_result: UpdateResult, step: Step) -> UpdateResult:
        """Run a step and return a result."""
        if _is_async_step(step):
            result = await step(prev_result.context)
        else:
            result = step(prev_result.context)
        return result

    def _handle_complete(self, context: InterviewContext) -> UpdateResult:
        if isinstance(context.state.target, ParentInterviewContext):
            parent_ctx = context.state.target.context
            value = (
                context.state.data
                if context.state.target.value is None
                else evaluate(context.state.target.value, context.state.data)
            )
            new_data = context.state.target.result.set(
                parent_ctx.state.template_context, value
            )
            return UpdateResult(
                parent_ctx.with_state(parent_ctx.state.update(data=new_data))
            )
        else:
            updated_state = context.state.update(completed=True)
            return UpdateResult(context.with_state(updated_state))


def _is_async_step(step: Step) -> TypeIs[AsyncStep]:
    func = getattr(step, "__call__", step)
    return iscoroutinefunction(func)
