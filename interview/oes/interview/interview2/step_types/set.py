"""Set step."""

from typing import Any

from attrs import frozen
from oes.interview.interview2.update import UpdateContext, UpdateResult
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import WhenCondition
from oes.utils.template import Expression


@frozen
class SetStep:
    """Set a value."""

    set: ValuePointer
    value: Expression
    when: WhenCondition = ()

    def __call__(self, context: UpdateContext) -> UpdateResult:
        try:
            cur_value = self.set.evaluate(context.state.template_context)
        except LookupError:
            # no current value, so set it
            new_value = self._get_value(context)
            return self._set_value(context, new_value)
        else:
            # set the value if it is different
            new_value = self._get_value(context)
            if cur_value != new_value:
                return self._set_value(context, new_value)
            else:
                return UpdateResult(context.state)

    def _get_value(self, request: UpdateContext) -> Any:
        return self.value.evaluate(request.state.template_context)

    def _set_value(self, request: UpdateContext, value: object) -> UpdateResult:
        new_data = self.set.set(request.state.data, value)
        new_state = request.state.update(data=new_data)
        return UpdateResult(new_state)
