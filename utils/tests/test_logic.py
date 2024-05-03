import jinja2
import pytest
from cattrs import Converter
from cattrs.preconf.orjson import make_converter
from oes.utils.logic import (
    LogicAnd,
    LogicOr,
    ValueOrEvaluable,
    WhenCondition,
    evaluate,
    make_logic_unstructure_fn,
    make_value_or_evaluable_structure_fn,
    make_when_condition_structure_fn,
)
from oes.utils.template import Expression, make_expression_structure_fn


@pytest.fixture
def converter():
    env = jinja2.Environment()
    converter = make_converter()
    converter.register_structure_hook(Expression, make_expression_structure_fn(env))
    converter.register_structure_hook(
        ValueOrEvaluable, make_value_or_evaluable_structure_fn(converter)
    )
    converter.register_structure_hook(
        WhenCondition, make_when_condition_structure_fn(converter)
    )
    converter.register_unstructure_hook(LogicAnd, make_logic_unstructure_fn(converter))
    converter.register_unstructure_hook(LogicOr, make_logic_unstructure_fn(converter))
    return converter


@pytest.mark.parametrize(
    "v, expected",
    [
        ("a", 1),
        ("b", 0),
        (0, 0),
        (1, 1),
        ({"other": 1}, {"other": 1}),
        ({"and": ["a", "t"]}, True),
        ({"and": ["a", "f"]}, False),
        ({"or": ["a", "f"]}, True),
        ({"or": ["b", "f"]}, False),
        ({"or": [{"and": ["t", "f"]}]}, False),
        (["t", "f"], False),
        (["t", "a"], True),
    ],
)
def test_logic(converter: Converter, v, expected):
    context = {
        "a": 1,
        "b": 0,
        "t": True,
        "f": False,
    }
    structured = converter.structure(v, WhenCondition)  # type: ignore
    assert evaluate(structured, context) == expected


def test_unstructure_logic(converter: Converter):
    cond = LogicAnd(
        (
            LogicOr(
                (
                    1,
                    False,
                )
            ),
            True,
        )
    )
    unstructured = converter.unstructure(cond)
    assert unstructured == {
        "and": [
            {"or": [1, False]},
            True,
        ],
    }
