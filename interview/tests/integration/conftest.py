from collections.abc import Mapping
from typing import Optional

import orjson
import pytest
import pytest_asyncio
from blacksheep import Content, Response
from blacksheep.testing import TestClient
from oes.interview.config.interview import InterviewConfig, load_interviews
from oes.interview.serialization import converter
from oes.interview.server.app import make_app
from oes.interview.server.settings import Settings
from oes.interview.variables.env import jinja2_env
from oes.template import set_jinja2_env
from typed_settings import Secret


@pytest.fixture
def settings():
    return Settings(
        encryption_key=Secret(b"\0" * 32),
        api_key=Secret("changeit"),
    )


@pytest.fixture
def interview_config():
    with set_jinja2_env(jinja2_env):
        yield load_interviews(converter, "tests/test_data/interviews.yml")


@pytest_asyncio.fixture
async def app(settings: Settings, interview_config: InterviewConfig):
    app = make_app(settings, interview_config)
    await app.start()
    yield app
    await app.stop()


@pytest.fixture
def test_client(app):
    return TestClient(app)


async def start_interview(
    test_client: TestClient,
    settings: Settings,
    id: str,
    context: Optional[Mapping] = None,
    data: Optional[Mapping] = None,
) -> Mapping:
    res = await test_client.post(
        f"/interviews/{id}",
        headers={"Authorization": f"Bearer {settings.api_key.get_secret_value()}"},
        content=make_json(
            {
                "context": context or {},
                "data": data or {},
            }
        ),
    )
    await handle_errors(res)

    return await res.json()


async def update_interview(
    test_client: TestClient,
    state: str,
    responses: Optional[Mapping] = None,
) -> Mapping:
    res = await test_client.post(
        "/update",
        content=make_json(
            {
                "responses": responses or {},
                "state": state,
            }
        ),
    )
    await handle_errors(res)
    return await res.json()


async def get_result(
    test_client: TestClient,
    settings: Settings,
    state: str,
) -> Mapping:
    res = await test_client.post(
        "/result",
        headers={"Authorization": f"Bearer {settings.api_key.get_secret_value()}"},
        content=make_json(
            {
                "state": state,
            }
        ),
    )
    await handle_errors(res)
    return await res.json()


def make_json(obj: object) -> Content:
    return Content(
        b"application/json",
        orjson.dumps(obj),
    )


async def handle_errors(response: Response):
    if response.status > 200 or response.status >= 400:
        if response.declares_json():
            content = await response.json()
        elif response.declares_content_type(b"text/plain"):
            content = await response.text()
        else:
            content = await response.read()

        assert False, f"Response status {response.status}: {content}"
