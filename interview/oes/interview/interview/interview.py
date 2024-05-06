"""Interview module."""

from collections.abc import Iterable, Mapping, Sequence

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.immutable import immutable_mapping
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import Step


@frozen
class Interview:
    """An interview."""

    questions: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=immutable_mapping[str, QuestionTemplate]
    )
    steps: Sequence[Step] = field(default=(), converter=tuple[Step, ...])


@frozen
class InterviewContext:
    """Interview context."""

    state: InterviewState = field(factory=InterviewState)
    question_templates: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=immutable_mapping[str, QuestionTemplate]
    )
    steps: Sequence[Step] = field(default=(), converter=tuple[Step, ...])
    path_index: Mapping[Sequence[str | int], Sequence[str]] = field(
        default=immutabledict(),
        converter=immutable_mapping[Sequence[str | int], Sequence[str]],
    )


def make_interview_context(
    question_templates: Mapping[str, QuestionTemplate],
    steps: Iterable[Step],
    state: InterviewState,
) -> InterviewContext:
    """Make an :class:`InterviewContext`."""
    steps = tuple(steps)
    path_index = index_question_templates_by_path(question_templates.items())
    # indirect_path_index = index_question_templates_by_indirect_path(by_id.items())
    return InterviewContext(state, question_templates, steps, path_index)


def index_question_templates_by_path(
    question_templates: Iterable[tuple[str, QuestionTemplate]]
) -> dict[Sequence[str | int], tuple[str, ...]]:
    """Index :class:`QuestionTemplate` objects by the value paths they provide."""
    index = {}
    for id, question_template in question_templates:
        for path in question_template.provides:
            cur = index.get(path, ())
            index[path] = (*cur, id)
    return index
    # indirect_path_index: Mapping[
    #     Sequence[str | int],
    #     Sequence[tuple[str, Set[Sequence[str | int | ValuePointer]]]],
    # ] = field(default=immutabledict(), converter=lambda v: immutabledict(v))
