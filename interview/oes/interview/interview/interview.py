"""Interview module."""

from collections.abc import Iterable, Mapping, Sequence, Set

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.resolve import (
    index_question_templates_by_indirect_path,
    index_question_templates_by_path,
)
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import Step
from oes.interview.logic.types import ValuePointer


@frozen
class Interview:
    """An interview."""

    questions: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=lambda v: immutabledict(v)
    )
    steps: Sequence[Step] = field(default=(), converter=lambda v: tuple(v))


@frozen
class InterviewContext:
    """Interview context."""

    question_templates: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=lambda v: immutabledict(v)
    )
    steps: Sequence[Step] = field(default=(), converter=lambda v: tuple(v))
    path_index: Mapping[Sequence[str | int], Sequence[str]] = field(
        default=immutabledict(), converter=lambda v: immutabledict(v)
    )
    indirect_path_index: Mapping[
        Sequence[str | int],
        Sequence[tuple[str, Set[Sequence[str | int | ValuePointer]]]],
    ] = field(default=immutabledict(), converter=lambda v: immutabledict(v))
    state: InterviewState = field(factory=InterviewState)


def make_interview(
    questions: Iterable[QuestionTemplate], steps: Iterable[Step]
) -> Interview:
    """Make an :class:`Interview` object."""
    by_id = {
        q.id if q.id else _make_question_id(idx): q
        for idx, q in enumerate(questions, start=1)
    }
    steps = tuple(steps)
    return Interview(by_id, steps)


def make_interview_context(
    question_templates: Iterable[QuestionTemplate],
    steps: Iterable[Step],
    state: InterviewState,
) -> InterviewContext:
    """Make an :class:`InterviewContext`."""
    by_id = {
        q.id if q.id else _make_question_id(idx): q
        for idx, q in enumerate(question_templates, start=1)
    }
    steps = tuple(steps)
    path_index = index_question_templates_by_path(by_id.items())
    indirect_path_index = index_question_templates_by_indirect_path(by_id.items())
    return InterviewContext(by_id, steps, path_index, indirect_path_index, state=state)


def _make_question_id(idx: int) -> str:
    return f"q{idx}"
