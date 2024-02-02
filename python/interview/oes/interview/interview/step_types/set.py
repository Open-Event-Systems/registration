"""Set step."""
from __future__ import annotations

from typing import Literal, Union

from attr import frozen
from jinja2 import Undefined
from oes.interview.interview.result import StepResult
from oes.interview.interview.update import InterviewUpdate
from oes.interview.logic import ValuePointer, WhenCondition
from oes.template import Context, Evaluable, ValueOrEvaluable


@frozen
class SetStep:
    """Set a value."""

    set: ValuePointer
    """The value to set."""

    value: ValueOrEvaluable
    """The value to set."""

    when: WhenCondition = ()
    """``when`` conditions."""

    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        ctx = update.state.template_context
        is_set, cur_val = self._get_value(update.state.template_context)

        if isinstance(self.value, Evaluable):
            val = self.value.evaluate(ctx)
        else:
            val = self.value

        # call __bool__ just to trigger undefined errors
        bool(val)

        if not is_set or val != cur_val:
            new_data = self.set.set(update.state.data, val)

            changed = True
            updated_state = update.state.set_data(new_data)
        else:
            changed = False
            updated_state = update.state

        return StepResult(
            state=updated_state,
            changed=changed,
        )

    def _get_value(
        self, context: Context
    ) -> Union[tuple[Literal[False], None], tuple[Literal[True], object]]:
        try:
            val = self.set.evaluate(context)
            return (False, None) if isinstance(val, Undefined) else (True, val)
        except LookupError:
            return False, None
