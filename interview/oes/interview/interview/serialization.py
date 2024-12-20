"""Serialization module."""

from collections.abc import Callable, Mapping
from typing import Any

from cattrs import Converter
from oes.interview.interview.step_types.ask import AskStep
from oes.interview.interview.step_types.block import Block
from oes.interview.interview.step_types.ensure import EnsureStep
from oes.interview.interview.step_types.exit import ExitStep
from oes.interview.interview.step_types.http import HTTPRequestStep
from oes.interview.interview.step_types.set import SetStep
from oes.interview.interview.step_types.sub import SubStep


def make_step_structure_fn(  # noqa: CCR001
    converter: Converter,
) -> Callable[[Any, Any], Any]:
    """Make a function to structure a :class:`Step`."""

    def structure(v, t):
        if isinstance(v, Mapping):
            if "block" in v:
                return converter.structure(v, Block)
            elif "ask" in v:
                return converter.structure(v, AskStep)
            elif "exit" in v:
                return converter.structure(v, ExitStep)
            elif "set" in v:
                return converter.structure(v, SetStep)
            elif "ensure" in v:
                return converter.structure(v, EnsureStep)
            elif "sub" in v:
                return converter.structure(v, SubStep)
            elif "url" in v:
                return converter.structure(v, HTTPRequestStep)
        raise ValueError(f"Invalid step: {v}")

    return structure
