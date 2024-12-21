from unittest.mock import MagicMock, create_autospec, patch

import pytest
from httpx import AsyncClient
from oes.interview.immutable import make_immutable
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step_types.http import HTTPRequestStep
from oes.interview.logic.pointer import parse_pointer


@pytest.fixture
def state():
    return InterviewState(target="test", data={"a": {"b": "c"}}, context={"c": True})


@pytest.fixture
def context(state: InterviewState):
    return InterviewContext(state)


@pytest.fixture
def mock_client():
    mock_client = create_autospec(AsyncClient)
    mock_client.return_value = mock_client
    mock_client.__aenter__.return_value = mock_client
    res_mock = MagicMock()
    res_mock.json.return_value = {"ok": True}
    mock_client.__aenter__.return_value.post.return_value = res_mock
    with patch("oes.interview.interview.step_types.http.AsyncClient", mock_client):
        yield mock_client


@pytest.mark.asyncio
async def test_http_step(context: InterviewContext, mock_client: AsyncClient):
    step = HTTPRequestStep("test", parse_pointer("result"))
    result = await step(context)
    assert result.context.state.data == make_immutable(
        {"a": {"b": "c"}, "result": {"ok": True}}
    )
    mock_client.post.assert_called_with(  # type: ignore
        "test",
        content=b'{"data":{"a":{"b":"c"}},"context":{"c":true}}',
        headers={"Content-Type": "application/json"},
    )


@pytest.mark.asyncio
async def test_http_step_skip(context: InterviewContext, mock_client: AsyncClient):
    step = HTTPRequestStep("test", parse_pointer("a"))
    result = await step(context)
    assert result.context.state == context.state
    mock_client.post.assert_not_called()  # type: ignore
