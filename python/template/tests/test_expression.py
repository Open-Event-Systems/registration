import copy

import pytest
from cattrs.preconf.json import make_converter
from jinja2 import Undefined

from oes.template.expression import (
    Expression,
    structure_expression,
    unstructure_expression,
)

converter = make_converter()
converter.register_structure_hook(Expression, structure_expression)
converter.register_unstructure_hook(Expression, unstructure_expression)


@pytest.mark.parametrize(
    "src, context, value",
    [
        ("100", {}, 100),
        ("'str'", {}, "str"),
        ("1 + a + b", {"a": 2, "b": 3}, 6),
    ],
)
def test_expression(src, context, value):
    expr = Expression(src)
    res = expr.evaluate(context)
    assert res == value


def test_undefined():
    expr = Expression("missing")
    res = expr.evaluate({})
    assert isinstance(res, Undefined)


def test_copy():
    a = Expression("test == 1")
    b = copy.deepcopy(a)
    assert a == b


def test_convert():
    tmpl = Expression("test == 1")
    as_str = converter.unstructure(tmpl)
    assert as_str == "test == 1"
    other = converter.structure(as_str, Expression)
    assert other == tmpl
