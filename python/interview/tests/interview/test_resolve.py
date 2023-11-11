import pytest
from cattrs.preconf.json import make_converter
from oes.interview.input.field_types.text import TextField
from oes.interview.input.question import Question
from oes.interview.interview.interview import Interview
from oes.interview.interview.resolve import get_ask_result_for_variable
from oes.interview.interview.state import InterviewState
from oes.interview.logic import default_jinja2_env, parse_pointer
from oes.template import Expression, Template, set_jinja2_env

converter = make_converter()


@pytest.fixture(autouse=True)
def _jinja2_env():
    with set_jinja2_env(default_jinja2_env):
        yield


@pytest.fixture
def interview() -> Interview:
    return Interview(
        questions=(
            Question(
                id="set-a-1",
                fields=(
                    TextField(
                        set=parse_pointer("a"),
                    ),
                ),
                when=(Expression("use_a1 | default(true) is true"),),
            ),
            Question(
                id="set-a-2",
                fields=(
                    TextField(
                        set=parse_pointer("a"),
                    ),
                ),
                when=Expression("use_a2 | default(false) is true"),
            ),
            Question(id="set-b", fields=(TextField(set=parse_pointer("b")),)),
            Question(
                id="set-c",
                fields=(
                    TextField(label=Template("B is: {{ b }}"), set=parse_pointer("c")),
                ),
            ),
            Question(
                id="set-d",
                fields=(TextField(label=Template("Set D"), set=parse_pointer("d.a")),),
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
        ("c", "set-c", {"b": "x"}),
        ("d.a", "set-d", {"d": {}}),
    ),
)
def test_resolve(interview, val, expected, data):
    ptr = parse_pointer(val)

    state = InterviewState(interview=interview, data=data)

    id_, result = get_ask_result_for_variable(state, ptr)

    assert id_ == expected
