"""Ensure step."""

from collections.abc import Sequence

from attrs import frozen
from jinja2 import Undefined
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.update import UpdateResult
from oes.utils.logic import WhenCondition, evaluate
from oes.utils.template import Expression


@frozen
class EnsureStep:
    """A grouping of steps."""

    ensure: Expression | Sequence[Expression]
    when: WhenCondition = True

    def __call__(self, context: InterviewContext) -> UpdateResult:
        """Run the step."""
        items = self.ensure if isinstance(self.ensure, Sequence) else [self.ensure]
        for item in items:
            self._eval(item, context)
        return UpdateResult(context, None)

    def _eval(self, expr: Expression, context: InterviewContext):
        res = evaluate(expr, context.state.template_context)
        if isinstance(res, Undefined):
            res._fail_with_undefined_error()
