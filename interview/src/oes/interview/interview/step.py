"""Specific step types."""
from __future__ import annotations

import copy
from collections.abc import Callable, Iterable, Mapping, Sequence
from http.cookiejar import Cookie, CookieJar
from typing import ClassVar, Literal, Optional, Union

import httpx
from attrs import frozen
from cattrs import Converter
from cattrs.preconf.orjson import OrjsonConverter, make_converter
from oes.interview.input.logic import evaluate_whenable
from oes.interview.interview.error import InterviewError
from oes.interview.interview.interview import Step, StepResult
from oes.interview.interview.result import AskResult, ExitResult, ResultContent
from oes.interview.interview.state import InterviewState
from oes.interview.variables.locator import Locator, UndefinedError
from oes.interview.variables.undefined import Undefined
from oes.template import Context, Expression, Template, ValueOrEvaluable, evaluate
from oes.util import merge_dict


@frozen
class AskStep(Step):
    """Ask a question."""

    ask: str
    """The question ID."""

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions."""

    async def __call__(self, state: InterviewState) -> StepResult:
        # skip if the question was already asked
        if self.ask in state.answered_question_ids:
            return StepResult(state, changed=False)

        question = state.interview.questions_by_id.get(self.ask)
        if question is None:
            raise InterviewError(f"Question ID not found: {self.ask}")

        schema = question.get_schema(state.template_context)

        updated = state.set_question(question.id)

        return StepResult(
            state=updated,
            changed=True,
            content=AskResult(schema=schema),
        )


@frozen
class SetStep(Step):
    """Set a value."""

    set: Locator
    """The variable to set."""

    value: Expression
    """The value to set."""

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions."""

    async def __call__(self, state: InterviewState) -> StepResult:
        ctx = state.template_context
        is_set, cur_val = self._get_value(state.template_context)

        val = self.value.evaluate(ctx)

        if val != cur_val:
            new_data = merge_dict({}, copy.deepcopy(state.data))
            self.set.set(val, new_data)

            changed = True
            updated_state = state.set_data(new_data)
        else:
            changed = False
            updated_state = state

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
        except UndefinedError:
            return False, None


@frozen
class EvalStep(Step):
    """Ensure values are present."""

    eval: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]]
    """The value or values to evaluate."""

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions."""

    async def __call__(self, state: InterviewState) -> StepResult:
        ctx = state.template_context

        # call __bool__ just to raise an exception for undefined values

        if isinstance(self.eval, Sequence) and not isinstance(self.eval, str):
            for item in self.eval:
                bool(evaluate(item, ctx))
        else:
            bool(evaluate(self.eval, ctx))

        return StepResult(
            state=state,
            changed=False,
        )


@frozen
class ExitStep(Step):
    """Stop the interview."""

    exit: Template
    """The reason."""

    description: Optional[Template] = ""
    """An optional description."""

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions."""

    async def __call__(self, state: InterviewState) -> StepResult:
        ctx = state.template_context
        return StepResult(
            state=state,
            changed=True,
            content=ExitResult(
                title=self.exit.render(ctx),
                description=self.description.render(ctx) if self.description else None,
            ),
        )


class _NullCookieJar(CookieJar):
    def set_cookie(self, cookie: Cookie):
        return


@frozen
class HookStepResult:
    """The result body from a hook step."""

    state: InterviewState
    content: Optional[ResultContent] = None


@frozen
class HookStep(Step):
    """Invoke a webhook."""

    url: str
    """The hook URL."""

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions."""

    # a hack
    converter: ClassVar[OrjsonConverter] = make_converter()
    json_default: ClassVar[Callable[[object], object]] = lambda x: x
    client: ClassVar[httpx.AsyncClient] = httpx.AsyncClient(cookies=_NullCookieJar())

    async def __call__(self, state: InterviewState, /) -> StepResult:
        body = HookStep.converter.dumps(state, default=HookStep.json_default)
        res = await HookStep.client.post(
            self.url,
            headers={
                "Content-Type": "application/json",
            },
            content=body,
        )
        res.raise_for_status()
        if res.status_code == 204:
            return StepResult(state, False)
        else:
            res_body = self.converter.loads(res.content, HookStepResult)
            return StepResult(res_body.state, True, res_body.content)


@frozen
class Block(Step):
    """A block of steps."""

    block: Sequence[Step]

    when: Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]] = ()
    """``when`` conditions."""

    async def __call__(self, state: InterviewState) -> StepResult:
        return await handle_steps(state, self.block)


async def handle_steps(state: InterviewState, steps: Iterable[Step]) -> StepResult:
    """Handle interview steps."""
    ctx = state.template_context
    for step in steps:
        if evaluate_whenable(step, ctx):
            result = await step(state)
            if result.changed:
                return result

    return StepResult(state, changed=False)


def structure_step(converter: Converter, v: object, t: object) -> Callable[..., Step]:
    """Get a function to structure a :class:`Step`."""
    if isinstance(v, Mapping):
        step_cls = _get_step(v)
        if step_cls is not None:
            return converter.structure(v, step_cls)

    raise TypeError(f"Invalid step: {v}")


_step_map = {
    "ask": AskStep,
    "block": Block,
    "set": SetStep,
    "eval": EvalStep,
    "exit": ExitStep,
    "url": HookStep,
}


def _get_step(v: Mapping) -> Optional[type]:
    for k, cls in _step_map.items():
        if k in v:
            return cls
    return None
