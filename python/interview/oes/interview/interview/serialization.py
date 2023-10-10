"""Serialization functions."""
from __future__ import annotations

__all__ = [
    "structure_step",
    "make_interview_structure_fn",
    "make_interview_unstructure_fn",
    "make_interview_state_structure_fn",
    "make_interview_state_unstructure_fn",
]

from typing import Any, Callable, Mapping, Optional

from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from oes.interview.interview.interview import Interview
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step_types.ask import AskStep
from oes.interview.interview.step_types.block import Block
from oes.interview.interview.step_types.eval import EvalStep
from oes.interview.interview.step_types.exit import ExitStep
from oes.interview.interview.step_types.hook import HookStep
from oes.interview.interview.step_types.set import SetStep
from oes.interview.interview.types import Step


def structure_step(converter: Converter, v: object) -> Step:
    """Structure a :class:`Step`."""
    if isinstance(v, Mapping):
        step_cls = _get_step(v)
        if step_cls is not None:
            return converter.structure(v, step_cls)

    raise TypeError(f"Invalid step: {v}")


# def structure_step_result


_step_map = {
    "ask": AskStep,
    "block": Block,
    "set": SetStep,
    "eval": EvalStep,
    "exit": ExitStep,
    "url": HookStep,
}


def _get_step(v: Mapping) -> Optional[type]:
    for k, cls in _step_map.items():
        if k in v:
            return cls
    return None


def make_interview_structure_fn(
    converter: Converter,
) -> Callable[[Mapping[str, Any], Any], Interview]:
    """Get a function to structure a :class:`Interview`."""
    structure = make_dict_structure_fn(
        Interview, converter, _questions_by_id=override(omit=True)
    )
    return structure


def make_interview_unstructure_fn(
    converter: Converter,
) -> Callable[[Interview], Mapping[str, Any]]:
    """Get a function to unstructure a :class:`Interview`."""
    structure = make_dict_unstructure_fn(
        Interview,
        converter,
        _questions_by_id=override(omit=True),
    )
    return structure


def make_interview_state_structure_fn(
    converter: Converter,
) -> Callable[[Mapping[str, Any], Any], InterviewState]:
    """Get a function to structure an :class:`InterviewState`."""
    return make_dict_structure_fn(
        InterviewState,
        converter,
        _template_context=override(omit=True),
    )


def make_interview_state_unstructure_fn(
    converter: Converter,
) -> Callable[[InterviewState], Mapping[str, Any]]:
    """Get a function to unstructure an :class:`InterviewState`."""
    return make_dict_unstructure_fn(
        InterviewState,
        converter,
        _template_context=override(omit=True),
    )
