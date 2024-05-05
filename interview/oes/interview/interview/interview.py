"""Interview module."""

from collections.abc import Iterable, Mapping, Sequence

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.resolve import index_question_templates_by_path
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import Step


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
    # indirect_path_index: Mapping[
    #     Sequence[str | int],
    #     Sequence[tuple[str, Set[Sequence[str | int | ValuePointer]]]],
    # ] = field(default=immutabledict(), converter=lambda v: immutabledict(v))
    state: InterviewState = field(factory=InterviewState)


def make_interview(
    questions: Mapping[str, QuestionTemplate], steps: Iterable[Step]
) -> Interview:
    """Make an :class:`Interview` object."""
    steps = tuple(steps)
    return Interview(questions, steps)


def make_interview_context(
    question_templates: Mapping[str, QuestionTemplate],
    steps: Iterable[Step],
    state: InterviewState,
) -> InterviewContext:
    """Make an :class:`InterviewContext`."""
    steps = tuple(steps)
    path_index = index_question_templates_by_path(question_templates.items())
    # indirect_path_index = index_question_templates_by_indirect_path(by_id.items())
    return InterviewContext(question_templates, steps, path_index, state=state)


def _make_question_id(idx: int) -> str:
    return f"q{idx}"
