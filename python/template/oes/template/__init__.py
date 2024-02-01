"""OES Template Library."""

from oes.template.env import get_jinja2_env, set_jinja2_env
from oes.template.expression import (
    Expression,
    structure_expression,
    unstructure_expression,
)
from oes.template.logic import (
    LogicAnd,
    LogicNot,
    LogicObject,
    LogicObjectTypes,
    LogicOr,
    evaluate,
    make_logic_structure_fn,
    make_logic_unstructure_fn,
    make_value_or_evaluable_structure_fn,
)
from oes.template.template import Template, structure_template, unstructure_template
from oes.template.types import Context, Evaluable, ValueOrEvaluable

__all__ = [
    "get_jinja2_env",
    "set_jinja2_env",
    "Expression",
    "structure_expression",
    "unstructure_expression",
    "LogicAnd",
    "LogicOr",
    "LogicNot",
    "LogicObject",
    "LogicObjectTypes",
    "evaluate",
    "make_value_or_evaluable_structure_fn",
    "make_logic_structure_fn",
    "make_logic_unstructure_fn",
    "Template",
    "structure_template",
    "unstructure_template",
    "Context",
    "Evaluable",
    "ValueOrEvaluable",
    # modules
    "filters",
]
