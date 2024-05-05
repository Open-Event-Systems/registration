"""Interview config."""

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from attrs import field, frozen
from cattrs import Converter
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.types import Step


@frozen
class InterviewConfig:
    """Interview config entry."""

    questions: Sequence[Path | QuestionTemplate] = field(
        default=(), converter=tuple[Path | QuestionTemplate, ...]
    )
    """The questions to include."""

    steps: Sequence[Step] = field(default=(), converter=tuple[Step, ...])
    """The interview steps."""


@frozen(kw_only=True)
class InterviewConfigObject(InterviewConfig):
    """Interview config as an object."""

    id: str
    """The interview ID."""


def make_interview_config_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], Any]:
    """Make a function to structure interview config objects."""

    def structure(v, t):
        if isinstance(v, (str, Path)):
            return converter.structure(v, Path)
        else:
            return converter.structure(v, InterviewConfigObject)

    return structure
