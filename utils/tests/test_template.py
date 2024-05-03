import jinja2
import pytest
from cattrs import Converter
from cattrs.preconf.orjson import make_converter
from oes.utils.template import (
    Expression,
    Template,
    make_expression_structure_fn,
    make_template_structure_fn,
    unstructure_expression,
    unstructure_template,
)


@pytest.fixture
def converter():
    env = jinja2.Environment()
    converter = make_converter()
    converter.register_structure_hook(Expression, make_expression_structure_fn(env))
    converter.register_structure_hook(Template, make_template_structure_fn(env))
    converter.register_unstructure_hook(Expression, unstructure_expression)
    converter.register_unstructure_hook(Template, unstructure_template)
    return converter


def test_template(converter: Converter):
    template = converter.structure("value: {{ a }}", Template)
    result = template.render({"a": "rendered"})
    assert result == "value: rendered"
    to_str = converter.unstructure(template)
    assert to_str == "value: {{ a }}"


def test_expression(converter: Converter):
    expr = converter.structure("a + b", Expression)
    result = expr.evaluate({"a": 1, "b": 2})
    assert result == 3
    to_str = converter.unstructure(expr)
    assert to_str == "a + b"
