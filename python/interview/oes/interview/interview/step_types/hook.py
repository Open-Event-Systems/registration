"""Hook step."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

import orjson
from attr import frozen
from httpx import Response
from oes.interview.interview.result import StepResult
from oes.interview.interview.state import InterviewState
from oes.interview.interview.update import InterviewUpdate
from oes.interview.logic import ValuePointer, WhenCondition

if TYPE_CHECKING:
    from oes.interview.interview.step_types.ask import AskResult
    from oes.interview.interview.step_types.exit import ExitResult


@frozen
class HookStep:
    """Invoke a webhook."""

    url: str
    """The hook URL."""

    result: ValuePointer | None = None
    """An optional pointer to where to store result information."""

    when: WhenCondition = ()
    """``when`` conditions."""

    async def __call__(self, update: InterviewUpdate, /) -> StepResult:
        if not self._get_should_run(update.state):
            return StepResult(update.state, False, None)

        as_obj = update.converter.unstructure(update.state)
        body = orjson.dumps(as_obj, default=update.json_default)

        res = await update.http_client.post(
            self.url,
            headers={
                "Content-Type": "application/json",
            },
            content=body,
        )

        res.raise_for_status()
        if res.status_code == 204:
            updated_state = self._set_result_info(update.state, res)
            # return changed=True if the result is being stored
            return StepResult(updated_state, self.result is not None)
        else:
            res_json = orjson.loads(res.content)
            res_obj = update.converter.structure(res_json, HookStepResult)
            updated_state = self._set_result_info(res_obj.state, res)
            return StepResult(updated_state, True, res_obj.content)

    def _get_should_run(self, state: InterviewState) -> bool:
        if self.result is None:
            return True

        try:
            val = self.result.evaluate(state.template_context)
        except LookupError:
            return True

        return not isinstance(val, Mapping) or val.get("success") is not True

    def _set_result_info(self, state: InterviewState, res: Response):
        if not self.result:
            return state

        info = {
            "status_code": res.status_code,
            "success": 200 <= res.status_code < 400,
        }

        updated_data = self.result.set(state.data, info)
        return state.set_data(updated_data)


@frozen
class HookStepResult:
    """The result body from a hook step."""

    state: InterviewState
    content: AskResult | ExitResult | None = None


# avoid circular imports
from oes.interview.interview.step_types.ask import AskResult  # noqa
from oes.interview.interview.step_types.exit import ExitResult  # noqa
