import pytest
from oes.interview.logic import UndefinedError, default_jinja2_env, parse_pointer
from oes.interview.logic.undefined import Undefined
from oes.template import Expression, Template, set_jinja2_env


@pytest.fixture(autouse=True)
def _jinja2_env():
    with set_jinja2_env(default_jinja2_env):
        yield


def test_undefined_defined():
    tmpl = Template("a: {{ a }}, b: {{ b }}")

    assert tmpl.render({"a": 1, "b": 2}) == "a: 1, b: 2"


def test_undefined_1():
    tmpl = Template("a: {{ a }}, b: {{ b }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": 1})
    assert e.value.pointer == parse_pointer("b")


def test_undefined_2():
    tmpl = Template("{{ a.b }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": {}})
    assert e.value.pointer == parse_pointer("a.b")


def test_undefined_3():
    tmpl = Template("{{ a[1] }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": [0]})
    assert e.value.pointer == parse_pointer("a[1]")


def test_expression_defined():
    expr = Expression("a + b")
    assert expr.evaluate({"a": 1, "b": 2}) == 3


def test_expression_undefined_1():
    expr = Expression("a + b")

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1})

    assert e.value.pointer == parse_pointer("b")


def test_expression_undefined_2():
    expr = Expression("a + b.c")

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1, "b": {"d": 2}})

    assert e.value.pointer == parse_pointer("b.c")


def test_expression_missing():
    expr = Expression("a")
    res = expr.evaluate({})
    assert isinstance(res, Undefined)


@pytest.mark.parametrize(
    "expr, expected",
    (
        ("a | default(1)", 1),
        ("b | default(1)", True),
        ("c.e | default(2)", 2),
        ("e[1] | default(0)", 0),
    ),
)
def test_default_works(expr, expected):
    e = Expression(expr)

    assert e.evaluate({"b": True, "c": {"d": 3}, "e": [4]}) == expected
