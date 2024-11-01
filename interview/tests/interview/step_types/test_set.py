import pytest
from oes.interview.immutable import make_immutable
from oes.interview.interview.interview import InterviewContext
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step_types.set import SetStep
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.pointer import parse_pointer
from oes.interview.logic.proxy import ProxyLookupError
from oes.interview.logic.undefined import UndefinedError
from oes.utils.template import Expression


@pytest.fixture
def state():
    return InterviewState(target="test", data={"a": {"b": "c"}}, context={"c": True})


def test_set(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("'y'", default_jinja2_env))
    result = step(context)
    assert result.context.state.data == make_immutable({"a": {"b": "c", "x": "y"}})


def test_set_referencing_context(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("c", default_jinja2_env))
    result = step(context)
    assert result.context.state.data == make_immutable({"a": {"b": "c", "x": True}})


def test_set_diff(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.b"), Expression("1", default_jinja2_env))
    result = step(context)
    assert result.context.state.data == make_immutable({"a": {"b": 1}})


def test_set_no_diff(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.b"), Expression("'c'", default_jinja2_env))
    result = step(context)
    assert result.context.state == state


def test_set_raises_proxy_error(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("y", default_jinja2_env))
    with pytest.raises(ProxyLookupError) as err:
        step(context)
    assert err.value.path == ()
    assert err.value.key == "y"


def test_set_raises_proxy_error_2(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("a.z", default_jinja2_env))
    with pytest.raises(ProxyLookupError) as err:
        step(context)
    assert err.value.path == ("a",)
    assert err.value.key == "z"


def test_set_raises_undefined_error(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.x"), Expression("y.z", default_jinja2_env))
    with pytest.raises(UndefinedError) as err:
        step(context)
    assert err.value.path == ()
    assert err.value.key == "y"


def test_set_raises_undefined_error_from_set(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("x.y"), Expression("1", default_jinja2_env))
    with pytest.raises(ProxyLookupError) as err:
        step(context)
    assert err.value.path == ()
    assert err.value.key == "x"


def test_set_raises_undefined_error_from_set_2(state: InterviewState):
    context = InterviewContext(state=state)
    step = SetStep(parse_pointer("a.c.d"), Expression("1", default_jinja2_env))
    with pytest.raises(ProxyLookupError) as err:
        step(context)
    assert err.value.path == ("a",)
    assert err.value.key == "c"
