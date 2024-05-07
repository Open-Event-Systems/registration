import os

import pytest
import pytest_asyncio
from cattrs.preconf.orjson import make_converter
from oes.interview.cache import CacheService
from oes.interview.input.field_types.text import TextFieldTemplate
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.interview import make_interview_context
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step_types.exit import ExitStep
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.pointer import parse_pointer
from oes.interview.serialization import configure_converter
from oes.utils.template import Expression, Template


@pytest_asyncio.fixture
async def cache():
    redis_url = os.getenv("TEST_REDIS_URL", "")
    if not redis_url:
        pytest.skip("set TEST_REDIS_URL to enable")
    converter = make_converter()
    configure_converter(converter)
    cache = CacheService(redis_url, converter)
    async with cache:
        yield cache


@pytest.mark.asyncio
async def test_cache(cache: CacheService):
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
    )
    key = await cache.put(context)
    retrieved = await cache.get(key)
    assert retrieved == context
