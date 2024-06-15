import os

import pytest
import pytest_asyncio
from cattrs.preconf.orjson import make_converter
from oes.interview.input.field_types.text import TextFieldTemplate
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.interview import make_interview_context
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step_types.exit import ExitStep
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.pointer import parse_pointer
from oes.interview.serialization import configure_converter
from oes.interview.storage import StorageService
from oes.utils.template import Expression, Template


@pytest_asyncio.fixture
async def storage():
    redis_url = os.getenv("TEST_REDIS_URL", "")
    if not redis_url:
        pytest.skip("set TEST_REDIS_URL to enable")
    converter = make_converter()
    configure_converter(converter)
    storage = StorageService(redis_url, converter)
    async with storage:
        yield storage


@pytest.mark.asyncio
async def test_storage(storage: StorageService):
    context = make_interview_context(
        {
            "q1": QuestionTemplate(
                title=Template("Test Question", default_jinja2_env),
                description=Template("Test template", default_jinja2_env),
                fields={parse_pointer("test"): TextFieldTemplate()},
            ),
        },
        steps=(
            ExitStep(
                Template("exit", default_jinja2_env),
                when=Expression("value == 0", default_jinja2_env),
            ),
        ),
        state=InterviewState(context={"value": 0}),
        interviews={},
    )
    key = await storage.put(context)
    retrieved = await storage.get(key)
    assert retrieved == context
