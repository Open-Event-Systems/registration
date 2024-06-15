"""Block step."""

from collections.abc import Sequence
from inspect import iscoroutinefunction

from attrs import frozen
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.types import AsyncStep, Step
from oes.interview.interview.update import UpdateResult
from oes.interview.logic.proxy import make_proxy
from oes.utils.logic import WhenCondition, evaluate
from typing_extensions import TypeIs


@frozen
class Block:
    """A grouping of steps."""

    block: Sequence[Step]
    when: WhenCondition = True

    async def __call__(self, context: InterviewContext) -> UpdateResult:
        """Run the steps."""
        ctx = make_proxy(context.state.template_context)
        cur_result = UpdateResult(context)
        for step in self.block:
            if not evaluate(step.when, ctx):
                continue
            next_result = await _run_step(cur_result, step)
            if (
                next_result.content is not None
                or next_result.context.state is not cur_result.context.state
                and next_result.context.state != cur_result.context.state
            ):
                return next_result
            cur_result = next_result
        else:
            return cur_result


async def _run_step(prev_result: UpdateResult, step: Step) -> UpdateResult:
    """Run a step and return a result."""
    if _is_async_step(step):
        result = await step(prev_result.context)
    else:
        result = step(prev_result.context)
    return result


def _is_async_step(step: Step) -> TypeIs[AsyncStep]:
    func = getattr(step, "__call__", step)
    return iscoroutinefunction(func)
