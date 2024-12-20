"""Interview module."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from attrs import evolve, field, frozen
from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from immutabledict import immutabledict
from oes.interview.immutable import immutable_mapping
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import Step
from typing_extensions import Self


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

    state: InterviewState
    question_templates: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=immutable_mapping[str, QuestionTemplate]
    )
    steps: Sequence[Step] = field(default=(), converter=tuple[Step, ...])
    path_index: Mapping[Sequence[str | int], Sequence[str]] = field(
        default=immutabledict(),
        converter=immutable_mapping[Sequence[str | int], Sequence[str]],
    )
    interviews: Mapping[str, Interview] = field(
        default=immutabledict(), converter=immutable_mapping[str, Interview]
    )

    def with_state(self, state: InterviewState) -> Self:
        """Return a copy with the state replaced."""
        return evolve(self, state=state)


def make_interview_context(
    question_templates: Mapping[str, QuestionTemplate],
    steps: Iterable[Step],
    state: InterviewState,
    interviews: Mapping[str, Interview],
) -> InterviewContext:
    """Make an :class:`InterviewContext`."""
    steps = tuple(steps)
    path_index = index_question_templates_by_path(question_templates.items())
    # indirect_path_index = index_question_templates_by_indirect_path(by_id.items())
    return InterviewContext(state, question_templates, steps, path_index, interviews)


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


def make_interview_context_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], Any]:
    """Make a function to structure a :class:`InterviewContext`."""

    def structure_index(v, t):
        path_index_items = converter.structure(
            v,
            tuple[tuple[tuple[str | int, ...], tuple[str, ...]], ...],
        )
        return immutabledict(path_index_items)

    dict_fn = make_dict_structure_fn(
        InterviewContext, converter, path_index=override(struct_hook=structure_index)
    )

    return dict_fn


def make_interview_context_unstructure_fn(converter: Converter) -> Callable[[Any], Any]:
    """Make a function to unstructure a :class:`InterviewContext`."""
    dict_fn = make_dict_unstructure_fn(
        InterviewContext, converter, path_index=override(omit=True)
    )

    def unstructure(v: InterviewContext) -> Any:
        as_dict = dict_fn(v)
        as_dict["path_index"] = list(v.path_index.items())
        return as_dict

    return unstructure
