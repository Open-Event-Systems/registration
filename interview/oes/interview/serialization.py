"""Serialization module."""

from pathlib import Path
from typing import Union

from cattrs import Converter
from cattrs.preconf.orjson import make_converter
from oes.interview.input.types import FieldTemplate
from oes.interview.logic.env import default_jinja2_env
from oes.utils.template import (
    Expression,
    Template,
    make_expression_structure_fn,
    make_template_structure_fn,
)

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
    from oes.interview.interview.serialization import make_step_structure_fn
    from oes.interview.interview.types import Step
    from oes.interview.logic.pointer import ValuePointer, parse_pointer

    converter.register_structure_hook(
        Template, make_template_structure_fn(default_jinja2_env)
    )
    converter.register_structure_hook(
        Expression, make_expression_structure_fn(default_jinja2_env)
    )

    converter.register_structure_hook(ValuePointer, lambda v, t: parse_pointer(v))
    converter.register_unstructure_hook(ValuePointer, lambda v: str(v))

    converter.register_structure_hook(
        FieldTemplate, make_field_template_structure_fn(converter)
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
