import pytest
from cattrs.preconf.json import make_converter
from oes.template.expression import (
    Expression,
    structure_expression,
    unstructure_expression,
)
from oes.template.logic import (
    LogicObject,
    LogicObjectTypes,
    evaluate,
    make_logic_structure_fn,
    make_logic_unstructure_fn,
    make_value_or_evaluable_structure_fn,
)
from oes.template.types import ValueOrEvaluable

converter = make_converter()
converter.register_structure_hook(Expression, structure_expression)
converter.register_structure_hook(
    ValueOrEvaluable, make_value_or_evaluable_structure_fn(converter)
)
converter.register_unstructure_hook(
    Expression,
    unstructure_expression,
)
converter.register_structure_hook_func(
    lambda cls: cls == LogicObject, make_logic_structure_fn(converter)
)
converter.register_unstructure_hook_func(
    lambda cls: cls in LogicObjectTypes,
    make_logic_unstructure_fn(converter),
)

cases = [
    (
        True,
        {},
        True,
    ),
    (
        False,
        {},
        False,
    ),
    (
        "0",
        {},
        False,
    ),
    (
        "false",
        {},
        False,
    ),
    (
        "value",
        {"value": False},
        False,
    ),
    (
        "value",
        {"value": True},
        True,
    ),
    (
        {
            "or": (
                "1 + 1 == 2",
                "0",
            )
        },
        {},
        True,
    ),
    (
        {
            "and": (
                "1 + 1 == 2",
                "0",
            )
        },
        {},
        False,
    ),
    (
        {"and": ("a + b == 10", {"or": "c"})},
        {"a": 5, "b": 5, "c": 0},
        False,
    ),
    (
        {"and": ("a + b == 10", {"or": "c"})},
        {"a": 5, "b": 4, "c": 1},
        False,
    ),
    (
        {"and": ("a + b == 10", {"or": "c"})},
        {"a": 5, "b": 5, "c": 1},
        True,
    ),
    (
        {"not": "value"},
        {"value": False},
        True,
    ),
    (
        {"not": {"not": "value"}},
        {"value": False},
        False,
    ),
]


@pytest.mark.parametrize(
    "src, context, value",
    cases,
)
def test_logic_parsing_and_eval(src, context, value):
    condition = converter.structure(src, ValueOrEvaluable)  # type: ignore
    result = evaluate(condition, context)
    assert result == value


@pytest.mark.parametrize(
    "case",
    [
        "a",
        {"and": ["a", 2]},
        ["a", {"or": [{"and": "1 + 1 == 2"}, 0]}],
    ],
)
def test_logic_parsing_unstructure(case):
    condition = converter.structure(case, ValueOrEvaluable)  # type: ignore
    back = converter.unstructure(condition, ValueOrEvaluable)
    assert back == case
