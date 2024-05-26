"""Block step."""

from collections.abc import Sequence

from attrs import frozen
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.types import Step
from oes.interview.interview.update import UpdateResult, run_steps
from oes.utils.logic import WhenCondition


@frozen
class Block:
    """A grouping of steps."""

    block: Sequence[Step]
    when: WhenCondition = True

    async def __call__(self, context: InterviewContext) -> UpdateResult:
        """Run the steps."""
        res, content = await run_steps(context, self.block)
        return UpdateResult(res.state, content)
