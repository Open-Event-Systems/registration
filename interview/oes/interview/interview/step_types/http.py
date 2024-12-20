"""HTTP request step."""

from attrs import frozen
from cattrs.preconf.orjson import make_converter
from httpx import AsyncClient
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.update import UpdateResult
from oes.interview.logic.proxy import make_proxy
from oes.interview.logic.types import ValuePointer
from oes.utils.logic import WhenCondition


@frozen
class HTTPRequestStep:
    """HTTP request step."""

    url: str
    result: ValuePointer
    when: WhenCondition = True

    async def __call__(self, context: InterviewContext) -> UpdateResult:
        try:
            self.result.evaluate(context.state.template_context)
        except LookupError:
            pass
        else:
            # no action if the result is already set
            return UpdateResult(context)

        body = self._get_body(context)
        async with AsyncClient() as client:
            res = await client.post(
                self.url, content=body, headers={"Content-Type": "application/json"}
            )
            res.raise_for_status()
            result_data = res.json()
        proxy = make_proxy(context.state.data)
        new_data = self.result.set(proxy, result_data)
        new_state = context.state.update(data=new_data)
        return UpdateResult(context.with_state(new_state))

    def _get_body(self, context: InterviewContext) -> bytes:
        body = {
            "data": context.state.data,
            "context": context.state.context,
        }
        body_bytes = _converter.dumps(body)
        return body_bytes


_converter = make_converter()
