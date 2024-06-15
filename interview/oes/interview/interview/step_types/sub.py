"""Sub-interview step."""

from collections.abc import Mapping
from typing import Any

from attrs import field, frozen
from immutabledict import immutabledict
from jinja2 import Undefined
from oes.interview.immutable import immutable_mapping
from oes.interview.interview.error import InterviewError
from oes.interview.interview.interview import (
    Interview,
    InterviewContext,
    make_interview_context,
)
from oes.interview.interview.state import InterviewState, ParentInterviewContext
from oes.interview.interview.update import UpdateResult
from oes.interview.logic.proxy import ProxyLookupError, make_proxy
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import ValueOrEvaluable, WhenCondition, evaluate
from oes.utils.template import TemplateContext


@frozen
class SubStep:
    """Start a sub-interview."""

    sub: str
    result: ValuePointer
    context: Mapping[str, ValueOrEvaluable] = field(
        default=immutabledict(), converter=immutable_mapping[str, ValueOrEvaluable]
    )
    initial_data: Mapping[str, ValueOrEvaluable] = field(
        default=immutabledict(), converter=immutable_mapping[str, ValueOrEvaluable]
    )
    when: WhenCondition = True

    def __call__(self, context: InterviewContext) -> UpdateResult:
        tmpl_ctx = make_proxy(context.state.template_context)
        try:
            cur_result = self.result.evaluate(tmpl_ctx)
        except LookupError:
            cur_result = None

        if cur_result is None:
            return self._start_interview(tmpl_ctx, context)
        else:
            return UpdateResult(context)

    def _start_interview(
        self, tmpl_ctx: TemplateContext, context: InterviewContext
    ) -> UpdateResult:
        interview = self._get_interview(context)
        new_context = _eval_mapping(tmpl_ctx, self.context)
        new_data = _eval_mapping(tmpl_ctx, self.initial_data)
        state = InterviewState(
            date_expires=context.state.date_expires,
            context={
                "parent_context": context.state.context,
                "parent_data": context.state.data,
                **new_context,
            },
            data=new_data,
            target=ParentInterviewContext(
                context,
                self.result,
            ),
        )

        new_interview_context = make_interview_context(
            interview.questions, interview.steps, state, context.interviews
        )

        return UpdateResult(new_interview_context)

    def _get_interview(self, context: InterviewContext) -> Interview:
        interview = context.interviews.get(self.sub)
        if not interview:
            raise InterviewError(f"Interview not found: {self.sub}")
        return interview


def _eval_mapping(
    tmpl_ctx: TemplateContext, mapping: Mapping[str, ValueOrEvaluable]
) -> Mapping[str, Any]:
    return {k: _eval_value(tmpl_ctx, v) for k, v in mapping.items()}


def _eval_value(tmpl_ctx: TemplateContext, e: ValueOrEvaluable) -> Any:
    res = evaluate(e, tmpl_ctx)
    if isinstance(res, Undefined):
        raise ProxyLookupError(res._key, res._path)
    else:
        return res
