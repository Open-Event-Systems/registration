"""Serialization module."""
from collections.abc import Callable, Sequence
from datetime import date, datetime
from functools import singledispatch
from pathlib import Path
from typing import Any, Tuple, Union, get_args, get_origin

from attrs import fields
from cattrs import Converter, override
from cattrs.gen import make_dict_unstructure_fn
from cattrs.preconf.orjson import make_converter
from oes.interview.config.interview import structure_question_or_path
from oes.interview.input.field import structure_field
from oes.interview.input.logic import structure_evaluable_or_sequence
from oes.interview.input.question import (
    Question,
    make_question_structure_fn,
    make_question_unstructure_fn,
)
from oes.interview.input.types import Field
from oes.interview.interview.interview import (
    Interview,
    Step,
    make_interview_structure_fn,
    make_interview_unstructure_fn,
)
from oes.interview.interview.state import (
    InterviewState,
    make_interview_state_structure_fn,
    make_interview_state_unstructure_fn,
)
from oes.interview.interview.step import structure_step
from oes.interview.variables.locator import Locator, parse_locator
from oes.template import (
    Expression,
    Template,
    ValueOrEvaluable,
    structure_expression,
    structure_template,
    structure_value_or_evaluable,
)
from oes.util import is_attrs_class, is_attrs_instance


@singledispatch
def json_default(obj: object) -> object:
    if is_attrs_instance(obj):
        return converter.unstructure(obj)
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


@json_default.register
def _(obj: datetime) -> str:
    return obj.isoformat(timespec="seconds")


@json_default.register
def _(obj: date) -> str:
    return obj.isoformat()


def configure_converter(converter: Converter):
    """Configure the given converter."""

    # omit None if it is the default
    converter.register_unstructure_hook_factory(
        lambda cls: is_attrs_class(cls),
        lambda cls: _make_unstructure_omit_none_fn(converter, cls),
    )

    converter.register_structure_hook(
        datetime,
        structure_datetime,
    )
    converter.register_structure_hook(
        date,
        structure_date,
    )
    converter.register_structure_hook(Template, structure_template)
    converter.register_structure_hook(Expression, structure_expression)
    converter.register_structure_hook(Locator, lambda v, t: parse_locator(v))

    converter.register_unstructure_hook(Template, lambda v: v.source)
    converter.register_unstructure_hook(Expression, lambda v: v.source)
    converter.register_unstructure_hook(Locator, lambda v: str(v))

    # structure immutable sequences as tuples
    converter.register_structure_hook_func(
        lambda cls: get_origin(cls) is Sequence,
        lambda v, t: converter.structure(v, Tuple[get_args(t)[0], ...]),
    )

    # handle Field
    converter.register_structure_hook_func(
        lambda cls: cls is Field, lambda v, t: structure_field(converter, v, t)
    )

    # expression strings or literal values
    converter.register_structure_hook_func(
        lambda cls: cls == ValueOrEvaluable,
        lambda v, t: structure_value_or_evaluable(converter, v, t),
    )

    converter.register_structure_hook_func(
        lambda cls: cls == Union[ValueOrEvaluable, Sequence[ValueOrEvaluable]],
        lambda v, t: structure_evaluable_or_sequence(converter, v, t),
    )

    # question
    converter.register_structure_hook(Question, make_question_structure_fn(converter))
    converter.register_unstructure_hook(
        Question, make_question_unstructure_fn(converter)
    )

    # path vs question
    converter.register_structure_hook_func(
        lambda cls: cls == Union[Path, Question],
        lambda v, t: structure_question_or_path(converter, v, t),
    )

    # steps
    converter.register_structure_hook_func(
        lambda cls: cls is Step, lambda v, t: structure_step(converter, v, t)
    )

    # interview
    converter.register_structure_hook(Interview, make_interview_structure_fn(converter))
    converter.register_unstructure_hook(
        Interview, make_interview_unstructure_fn(converter)
    )

    # interview state
    converter.register_structure_hook(
        InterviewState, make_interview_state_structure_fn(converter)
    )
    converter.register_unstructure_hook(
        InterviewState, make_interview_state_unstructure_fn(converter)
    )


def structure_date(obj: object, t: object) -> date:
    """Structure a :obj:`date`."""
    if isinstance(obj, date):
        return obj
    elif isinstance(obj, str):
        return date.fromisoformat(obj)
    else:
        raise TypeError(f"Invalid date: {obj}")


def structure_datetime(obj: object, t: object) -> datetime:
    """Structure a :obj:`datetime`."""
    if isinstance(obj, datetime):
        dt = obj
    elif isinstance(obj, str):
        dt = datetime.fromisoformat(_fix_timestamp(obj))
    elif isinstance(obj, (int, float)):
        dt = datetime.fromtimestamp(obj)
    else:
        raise TypeError(f"Invalid datetime: {obj}")

    return dt.astimezone() if dt.tzinfo is None else dt


def _make_unstructure_omit_none_fn(
    converter: Converter, t: Any
) -> Callable[[object], object]:
    overrides = {}

    for attr in fields(t):
        if attr.default is None:
            overrides[attr.name] = override(omit_if_default=True)

    return make_dict_unstructure_fn(t, converter, **overrides)


def _fix_timestamp(v: str) -> str:
    if v[-1] == "Z":
        return v[:-1] + "+00:00"
    else:
        return v


converter = make_converter()
"""The default converter."""

configure_converter(converter)
