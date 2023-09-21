"""OES Template Library"""

from oes.template.env import get_jinja2_env, set_jinja2_env
from oes.template.expression import (
    Expression,
    structure_expression,
    unstructure_expression,
)
from oes.template.functions import age_filter, date_filter
from oes.template.logic import (
    LogicAnd,
    LogicNot,
    LogicOr,
    evaluate,
    structure_logic,
    structure_value_or_evaluable,
    unstructure_logic,
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
    "evaluate",
    "structure_value_or_evaluable",
    "structure_logic",
    "unstructure_logic",
    "Template",
    "structure_template",
    "unstructure_template",
    "Context",
    "Evaluable",
    "ValueOrEvaluable",
    "age_filter",
    "date_filter",
]
