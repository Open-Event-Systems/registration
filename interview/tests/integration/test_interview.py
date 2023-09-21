import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from blacksheep.testing import TestClient
from oes.interview.interview.step import HookStep
from oes.interview.serialization import converter, json_default
from oes.interview.server.settings import Settings
from tests.integration.conftest import get_result, start_interview, update_interview


@pytest.mark.asyncio
async def test_interview_1(
    test_client: TestClient,
    settings: Settings,
):
    res = await start_interview(test_client, settings, "interview1")
    state = res["state"]
    assert res["content"] == {
        "schema": {
            "properties": {
                "field_0": {
                    "maxLength": 300,
                    "minLength": 0,
                    "title": "Name",
                    "type": "string",
                    "x-type": "text",
                    "nullable": False,
                }
            },
            "required": ["field_0"],
            "title": "Name",
            "type": "object",
        },
        "type": "question",
    }

    res = await update_interview(
        test_client,
        state,
        {
            "field_0": "Test",
        },
    )

    state = res["state"]
    assert res["complete"] is True

    result = await get_result(test_client, settings, state)
    assert result["data"] == {"name": "Test", "name2": "Test"}


@pytest.mark.asyncio
async def test_interview_2(
    test_client: TestClient,
    settings: Settings,
):
    res = await start_interview(
        test_client, settings, "interview2", data={"person": {}}
    )
    state = res["state"]

    res = await update_interview(
        test_client,
        state,
        {
            "field_0": "Test Name",
            "field_1": "1",
        },
    )

    state = res["state"]
    assert res["complete"] is True

    result = await get_result(test_client, settings, state)
    assert result["data"] == {
        "person": {
            "name": "Test Name",
        },
        "use_preferred_name": True,
    }


@pytest.mark.asyncio
@patch.object(HookStep, "client")
async def test_interview_3(
    client_mock,
    test_client: TestClient,
    settings: Settings,
):
    HookStep.json_default = json_default
    HookStep.converter = converter
    res_mock = Mock()
    res_mock.status_code = 200
    empty_res_mock = Mock()
    empty_res_mock.status_code = 204

    def side_effect(*args, content, **kwargs):
        state = json.loads(content)
        if state["data"].get("modified"):
            return empty_res_mock
        else:
            state["data"]["modified"] = True
            res_mock.content = json.dumps({"state": state}).encode()
            return res_mock

    client_mock.post = AsyncMock(side_effect=side_effect)

    res = await start_interview(test_client, settings, "interview3")
    state = res["state"]

    res = await update_interview(
        test_client,
        state,
        {
            "field_0": "1999-01-01",
        },
    )

    state = res["state"]
    assert res["content"]["type"] == "question"

    res = await update_interview(
        test_client,
        state,
        {
            "field_0": "2",
        },
    )

    state = res["state"]
    assert res["complete"] is True

    result = await get_result(test_client, settings, state)
    assert result["data"] == {
        "birth_date": "1999-01-01",
        "level": "vip",
        "modified": True,
    }
