from pathlib import Path

import pytest
from cattrs import Converter
from cattrs.preconf.orjson import make_converter
from oes.interview.config.config import load_config
from oes.interview.immutable import make_immutable
from oes.interview.interview.interview import InterviewContext, make_interview_context
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step_types.exit import ExitResult
from oes.interview.interview.update import update_interview
from oes.interview.serialization import configure_converter


@pytest.fixture
def converter():
    converter = make_converter()
    configure_converter(converter)
    return converter


@pytest.mark.parametrize(
    "interview_path, interview_id, responses, final_data",
    [
        (
            "tests/test_data/configs/config1.yml",
            "interview1",
            [],
            {},
        ),
        (
            "tests/test_data/configs/config1.yml",
            "interview-file1",
            [["fname"], ["lname"]],
            {"first_name": "fname", "last_name": "lname"},
        ),
        (
            "tests/test_data/configs/config1.yml",
            "simple-with-set",
            [["fname"], ["lname"]],
            {"first_name": "fname", "last_name": "lname", "full_name": "fname lname"},
        ),
        (
            "tests/test_data/configs/config1.yml",
            "question-triggering-question",
            [["fname"], ["lname"], ["2"]],
            False,
        ),
    ],
)
@pytest.mark.asyncio
async def test_interview(
    converter: Converter,
    interview_path: str,
    interview_id: str,
    responses: list[list],
    final_data: object,
):
    path = Path(interview_path)
    base_dir = path.parent
    cfg = load_config(path, converter)
    interview = cfg.get_interviews(base_dir, converter)[interview_id]
    interview_context = make_interview_context(
        interview.questions, interview.steps, InterviewState()
    )

    responses = list(responses)
    final_state, content = await run_interview(interview_context, responses)
    if final_data is False:
        assert isinstance(content, ExitResult)
    else:
        assert content is None
        assert final_state.completed
        assert final_state.data == make_immutable(final_data)
        assert len(responses) == 0


async def run_interview(
    interview_context: InterviewContext, responses: list[list]
) -> tuple[InterviewState, object | None]:
    interview_context, content = await update_interview(interview_context)
    while not interview_context.state.completed:
        response_values = responses.pop(0)
        response = {f"field_{i}": v for i, v in enumerate(response_values)}

        interview_context, content = await update_interview(interview_context, response)
        if isinstance(content, ExitResult):
            return interview_context.state, content
    return interview_context.state, None
