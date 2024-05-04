import pytest
from oes.interview.logic.env import default_jinja2_env
from oes.interview.logic.undefined import Undefined, UndefinedError
from oes.utils.template import Expression, Template


def test_undefined_defined():
    tmpl = Template("a: {{ a }}, b: {{ b }}", default_jinja2_env)

    assert tmpl.render({"a": 1, "b": 2}) == "a: 1, b: 2"


def test_undefined_1():
    tmpl = Template("a: {{ a }}, b: {{ b }}", default_jinja2_env)

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": 1})
    assert e.value.path == ()
    assert e.value.key == "b"


def test_undefined_2():
    tmpl = Template("{{ a.b }}", default_jinja2_env)

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": {}})
    assert e.value.path == ("a",)
    assert e.value.key == "b"


def test_undefined_3():
    tmpl = Template("{{ a[1] }}", default_jinja2_env)

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": [0]})
    assert e.value.path == ("a",)
    assert e.value.key == 1


def test_expression_defined():
    expr = Expression("a + b", default_jinja2_env)
    assert expr.evaluate({"a": 1, "b": 2}) == 3


def test_expression_undefined_1():
    expr = Expression("a + b", default_jinja2_env)

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1})

    assert e.value.path == ()
    assert e.value.key == "b"


def test_expression_undefined_2():
    expr = Expression("a + b.c", default_jinja2_env)

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1, "b": {"d": 2}})

    assert e.value.path == ("b",)
    assert e.value.key == "c"


def test_expression_missing():
    expr = Expression("a", default_jinja2_env)
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
    e = Expression(expr, default_jinja2_env)

    assert e.evaluate({"b": True, "c": {"d": 3}, "e": [4]}) == expected
