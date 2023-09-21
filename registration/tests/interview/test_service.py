import json
from datetime import datetime, timezone
from unittest.mock import create_autospec

import httpx
import pytest
from oes.registration.interview.models import InterviewListItem
from oes.registration.interview.service import InterviewService
from oes.registration.models.config import Config
from tests.util import get_mock_http_client
from typed_settings import Secret


@pytest.fixture
def config():
    config = create_autospec(Config)
    config.interview.url = "http://localhost"
    config.interview.api_key = Secret("test_key")
    return config


@pytest.mark.asyncio
async def test_list_interviews(config, converter):
    async def handler(request):
        return httpx.Response(
            200,
            json=[
                {"id": "http://localhost/interviews/test1", "title": "Test 1"},
                {"id": "http://localhost/interviews/test2", "title": "Test 2"},
            ],
        )

    service = InterviewService(config, get_mock_http_client(handler), converter)
    results = await service.get_interviews()

    assert list(results) == [
        InterviewListItem(
            id="http://localhost/interviews/test1",
            title="Test 1",
        ),
        InterviewListItem(
            id="http://localhost/interviews/test2",
            title="Test 2",
        ),
    ]


@pytest.mark.asyncio
async def test_start_interview(config, converter):
    async def handler(request):
        assert json.loads(request.content) == {
            "context": {"test": 1},
            "data": {"item": 2},
            "submission_id": "s1",
            "target_url": "http://localhost/target",
        }

        return httpx.Response(
            200,
            json={
                "state": "xxxxx",
                "complete": False,
                "content": {},
                "update_url": "http://localhost/update",
            },
        )

    service = InterviewService(config, get_mock_http_client(handler), converter)
    results = await service.start_interview(
        "http://localhost/interviews/test1",
        target_url="http://localhost/target",
        submission_id="s1",
        context={"test": 1},
        initial_data={"item": 2},
    )

    assert results == {
        "state": "xxxxx",
        "complete": False,
        "content": {},
        "update_url": "http://localhost/update",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_body, status,valid",
    [
        ({"target_url": "http://localhost/target"}, 200, True),
        ({"complete": False, "target_url": "http://localhost/target"}, 200, False),
        (
            {
                "expiration_date": "2020-01-01T11:00:00+00:00",
                "target_url": "http://localhost/target",
            },
            200,
            False,
        ),
        (
            {
                "target_url": "http://localhost/other",
            },
            200,
            False,
        ),
        (
            {"target_url": "http://localhost/target"},
            400,
            False,
        ),
    ],
)
async def test_get_result(response_body, status, valid, config, converter):
    async def handler(request):
        return httpx.Response(
            status,
            json={
                "interview": {},
                "submission_id": "1",
                "expiration_date": "2020-01-01T12:00:00+00:00",
                "complete": True,
                "context": {},
                "data": {},
                **response_body,
            },
        )

    service = InterviewService(config, get_mock_http_client(handler), converter)
    result = await service.get_result(
        "xxxxx",
        target_url="http://localhost/target",
        now=datetime(2020, 1, 1, 11, tzinfo=timezone.utc),
    )

    if valid:
        assert result.complete is True
    else:
        assert result is None
