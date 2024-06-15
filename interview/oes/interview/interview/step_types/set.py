"""Set step."""

from typing import Any

from attrs import frozen
from jinja2 import Undefined as Jinja2Undefined
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.update import UpdateResult
from oes.interview.logic.proxy import ProxyLookupError, make_proxy
from oes.interview.logic.types import ValuePointer
from oes.interview.logic.undefined import Undefined
from oes.utils.logic import WhenCondition
from oes.utils.template import Expression, TemplateContext


@frozen
class SetStep:
    """Set a value."""

    set: ValuePointer
    value: Expression
    when: WhenCondition = True

    def __call__(self, context: InterviewContext) -> UpdateResult:
        proxy = make_proxy(context.state.template_context)
        try:
            cur_value = self.set.evaluate(proxy)
        except LookupError:
            # no current value, so set it
            new_value = self._get_value(proxy)
            return self._set_value(context, new_value)
        else:
            # set the value if it is different
            new_value = self._get_value(proxy)
            if isinstance(cur_value, Jinja2Undefined) or cur_value != new_value:
                return self._set_value(context, new_value)
            else:
                return UpdateResult(context)

    def _get_value(self, ctx: TemplateContext) -> Any:
        value = self.value.evaluate(ctx)
        if isinstance(value, Undefined):
            raise ProxyLookupError(value._key, value._path)
        return value

    def _set_value(self, context: InterviewContext, value: object) -> UpdateResult:
        proxy = make_proxy(context.state.data)
        new_data = self.set.set(proxy, value)
        new_state = context.state.update(data=new_data)
        return UpdateResult(context.with_state(new_state))
