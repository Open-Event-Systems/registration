import pytest
from cattrs.preconf.json import make_converter
from oes.interview.input.field_types.text import TextField
from oes.interview.input.question import Question
from oes.interview.interview.interview import Interview
from oes.interview.interview.resolve import get_ask_result_for_variable
from oes.interview.interview.state import InterviewState
from oes.interview.variables.env import jinja2_env
from oes.interview.variables.locator import parse_locator
from oes.template import Expression, Template, set_jinja2_env

converter = make_converter()


@pytest.fixture(autouse=True)
def _jinja2_env():
    with set_jinja2_env(jinja2_env):
        yield


@pytest.fixture
def interview() -> Interview:
    return Interview(
        questions=(
            Question(
                id="set-a-1",
                fields=(
                    TextField(
                        set=parse_locator("a"),
                    ),
                ),
                when=(Expression("use_a1 | default(true) is true"),),
            ),
            Question(
                id="set-a-2",
                fields=(
                    TextField(
                        set=parse_locator("a"),
                    ),
                ),
                when=Expression("use_a2 | default(false) is true"),
            ),
            Question(id="set-b", fields=(TextField(set=parse_locator("b")),)),
            Question(
                id="set-c",
                fields=(
                    TextField(label=Template("B is: {{ b }}"), set=parse_locator("c")),
                ),
            ),
        )
    )


@pytest.mark.parametrize(
    "val, expected, data",
    (
        ("a", "set-a-1", {}),
        ("a", "set-a-1", {"use_a2": True}),
        ("a", "set-a-2", {"use_a1": False, "use_a2": True}),
        ("b", "set-b", {}),
        ("c", "set-b", {}),
        ("c", "set-c", {"b": "x"}),
    ),
)
def test_resolve(interview, val, expected, data):
    loc = parse_locator(val)

    state = InterviewState(interview=interview, data=data)

    id_, result = get_ask_result_for_variable(state, loc)

    assert id_ == expected
