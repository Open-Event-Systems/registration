import pytest
from oes.interview.variables.env import jinja2_env
from oes.interview.variables.locator import Index, UndefinedError, Variable
from oes.interview.variables.undefined import Undefined
from oes.template import Expression, Template, set_jinja2_env


@pytest.fixture(autouse=True)
def _jinja2_env():
    with set_jinja2_env(jinja2_env):
        yield


def test_undefined_defined():
    tmpl = Template("a: {{ a }}, b: {{ b }}")

    assert tmpl.render({"a": 1, "b": 2}) == "a: 1, b: 2"


def test_undefined_1():
    tmpl = Template("a: {{ a }}, b: {{ b }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": 1})
    assert e.value.locator == Variable("b")


def test_undefined_2():
    tmpl = Template("{{ a.b }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": {}})
    assert e.value.locator == Index(Variable("a"), "b")


def test_undefined_3():
    tmpl = Template("{{ a[1] }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": [0]})
    assert e.value.locator == Index(Variable("a"), 1)


def test_undefined_4():
    tmpl = Template("{{ a[b] }}")

    assert tmpl.render({"a": {"x": "yes"}, "b": "x"}) == "yes"


def test_undefined_5():
    tmpl = Template("{{ a[b] }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": {"x": "yes"}, "b": "y"})

    assert e.value.locator == Index(Variable("a"), "y")


def test_undefined_6():
    tmpl = Template("{{ a[b] }}")

    with pytest.raises(UndefinedError) as e:
        tmpl.render({"a": {"x": "yes"}})

    assert isinstance(e.value.locator, Index)
    assert e.value.locator.target == Variable("a")
    assert type(e.value.locator.index) is Undefined


def test_expression_defined():
    expr = Expression("a + b")
    assert expr.evaluate({"a": 1, "b": 2}) == 3


def test_expression_undefined_1():
    expr = Expression("a + b")

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1})

    assert e.value.locator == Variable("b")


def test_expression_undefined_2():
    expr = Expression("a + b.c")

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1, "b": {"d": 2}})

    assert e.value.locator == Index(Variable("b"), "c")


def test_expression_undefined_3():
    expr = Expression("a + b[c]")

    with pytest.raises(UndefinedError) as e:
        expr.evaluate({"a": 1, "b": {"d": 2}})

    assert isinstance(e.value.locator, Index)
    assert e.value.locator.target == Variable("b")
    assert type(e.value.locator.index) is Undefined


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
