"""Serialization module."""

from pathlib import Path
from typing import Union

from cattrs import Converter
from cattrs.preconf.orjson import make_converter

converter = make_converter()


def configure_converter(converter: Converter):
    """Configure a :class:`Converter`."""
    from oes.interview.config.interview import (
        InterviewConfigObject,
        QuestionTemplateObject,
        make_interview_config_structure_fn,
        make_question_template_structure_fn,
    )
    from oes.interview.input.serialization import make_field_template_structure_fn
    from oes.interview.input.types import FieldTemplate
    from oes.interview.interview.interview import (
        InterviewContext,
        make_interview_context_structure_fn,
        make_interview_context_unstructure_fn,
    )
    from oes.interview.interview.serialization import make_step_structure_fn
    from oes.interview.interview.types import Step
    from oes.interview.logic.env import default_jinja2_env
    from oes.interview.logic.pointer import ValuePointer, parse_pointer
    from oes.utils.logic import (
        LogicAnd,
        LogicOr,
        ValueOrEvaluable,
        WhenCondition,
        make_logic_unstructure_fn,
        make_value_or_evaluable_structure_fn,
        make_when_condition_structure_fn,
    )
    from oes.utils.template import (
        Expression,
        Template,
        make_expression_structure_fn,
        make_template_structure_fn,
        unstructure_expression,
        unstructure_template,
    )

    converter.register_structure_hook(
        Template, make_template_structure_fn(default_jinja2_env)
    )
    converter.register_unstructure_hook(Template, unstructure_template)
    converter.register_structure_hook(
        Expression, make_expression_structure_fn(default_jinja2_env)
    )
    converter.register_unstructure_hook(Expression, unstructure_expression)

    template_structure_fn = make_template_structure_fn(default_jinja2_env)
    converter.register_structure_hook_func(
        lambda cls: cls == Union[str, Template, None],
        lambda v, t: template_structure_fn(v, t) if v is not None else None,
    )
    converter.register_structure_hook(
        ValueOrEvaluable, make_value_or_evaluable_structure_fn(converter)
    )
    converter.register_unstructure_hook_func(
        lambda cls: cls in (LogicAnd, LogicOr), make_logic_unstructure_fn(converter)
    )

    converter.register_structure_hook(
        WhenCondition, make_when_condition_structure_fn(converter)
    )

    converter.register_structure_hook(ValuePointer, lambda v, t: parse_pointer(v))
    converter.register_unstructure_hook(ValuePointer, lambda v: str(v))

    converter.register_structure_hook_func(
        lambda cls: cls is FieldTemplate, make_field_template_structure_fn(converter)
    )

    converter.register_structure_hook(Step, make_step_structure_fn(converter))

    converter.register_structure_hook(
        Union[Path, InterviewConfigObject],
        make_interview_config_structure_fn(converter),
    )
    converter.register_structure_hook(
        Union[Path, QuestionTemplateObject],
        make_question_template_structure_fn(converter),
    )

    converter.register_structure_hook(
        InterviewContext, make_interview_context_structure_fn(converter)
    )
    converter.register_unstructure_hook(
        InterviewContext, make_interview_context_unstructure_fn(converter)
    )
