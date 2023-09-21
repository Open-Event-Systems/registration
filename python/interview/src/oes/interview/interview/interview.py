"""Interview module."""
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Mapping, Optional

from attrs import Factory, field, frozen
from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from oes.interview.input.question import Question
from oes.interview.input.types import Whenable
from oes.interview.interview.result import ResultContent
from typing_extensions import Protocol

if TYPE_CHECKING:
    from oes.interview.interview.state import InterviewState


@frozen
class StepResult:
    """The result of a step."""

    state: InterviewState
    """The updated :class:`InterviewState`."""

    changed: bool
    """Whether a change was made."""

    content: Optional[ResultContent] = None
    """Result content."""


class Step(Whenable, Protocol):
    """A step in an interview."""

    @abstractmethod
    async def __call__(self, state: InterviewState, /) -> StepResult:
        """Handle the step."""
        ...


@frozen(kw_only=True)
class Interview:
    """An interview."""

    id: Optional[str] = None
    """The interview ID."""

    title: Optional[str] = None
    """The interview title."""

    questions: Sequence[Question] = ()
    """The available questions in the interview."""

    steps: Sequence[Step] = ()
    """The steps."""

    _questions_by_id: Mapping[str, Question] = field(
        default=Factory(lambda s: _make_questions_by_id(s), takes_self=True),
        init=False,
        eq=False,
    )

    @property
    def questions_by_id(self) -> Mapping[str, Question]:
        """Questions by ID."""
        return dict(self._questions_by_id)


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


def _make_questions_by_id(interview: Interview) -> Mapping[str, Question]:
    return {q.id: q for q in interview.questions}
