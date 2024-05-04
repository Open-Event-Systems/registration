import pytest
from oes.interview.immutable import make_immutable
from oes.interview.interview2.state import InterviewState
from oes.interview.interview2.step_types.set import SetStep
from oes.interview.interview2.update import UpdateContext
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.pointer import parse_pointer
from oes.utils.template import Expression


@pytest.fixture
def state():
    return InterviewState(data={"a": {"b": "c"}}, context={"c": True})


def test_set(state: InterviewState):
    context = UpdateContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("'y'", default_jinja2_env))
    result = step(context)
    assert result.state.data == make_immutable({"a": {"b": "c", "x": "y"}})


def test_set_referencing_context(state: InterviewState):
    context = UpdateContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("c", default_jinja2_env))
    result = step(context)
    assert result.state.data == make_immutable({"a": {"b": "c", "x": True}})


def test_set_diff(state: InterviewState):
    context = UpdateContext(state=state)
    step = SetStep(parse_pointer("a.b"), Expression("1", default_jinja2_env))
    result = step(context)
    assert result.state.data == make_immutable({"a": {"b": 1}})


def test_set_no_diff(state: InterviewState):
    context = UpdateContext(state=state)
    step = SetStep(parse_pointer("a.b"), Expression("'c'", default_jinja2_env))
    result = step(context)
    assert result.state == state
