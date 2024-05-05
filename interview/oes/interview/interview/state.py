"""Interview state module."""

from collections.abc import Iterable, Mapping, Set
from datetime import datetime, timedelta
from typing import Any

from attrs import Factory, evolve, field, frozen
from immutabledict import immutabledict
from oes.interview.immutable import immutable_converter, make_immutable
from oes.interview.input.question import Question
from oes.utils.template import TemplateContext
from typing_extensions import Self

_unset: Any = object()

DEFAULT_INTERVIEW_EXPIRATION = timedelta(hours=1)
"""Default interview expiration time."""


@frozen
class InterviewState:
    """An interview's state data."""

    date_started: datetime = field(factory=lambda: datetime.now().astimezone())
    date_expires: datetime = field(
        default=Factory(
            lambda s: s.date_started + DEFAULT_INTERVIEW_EXPIRATION, takes_self=True
        )
    )
    target: str | None = None
    context: Mapping[str, Any] = field(
        default=immutabledict(), converter=immutable_converter(Mapping[str, Any])
    )
    data: Mapping[str, Any] = field(
        default=immutabledict(), converter=immutable_converter(Mapping[str, Any])
    )
    completed: bool = False
    answered_question_ids: Set[str] = field(
        default=frozenset(), converter=frozenset[str]
    )
    current_question: Question | None = None

    _template_context: Mapping[str, Any] = field(
        init=False,
        repr=False,
        eq=False,
        default=Factory(lambda s: _merge_dict(s.data, s.context), takes_self=True),
    )

    @property
    def template_context(self) -> TemplateContext:
        """Combined context and data for use with template/expression evaluation."""
        return self._template_context

    def update(
        self,
        *,
        data: Mapping[str, Any] | None = None,
        completed: bool | None = None,
        answered_question_ids: Iterable[str] = _unset,
        current_question: Question | None = _unset,
    ) -> Self:
        """Return an updated interview state."""
        new_data = data if data is not None else self.data
        new_question_ids = (
            frozenset(answered_question_ids)
            if answered_question_ids is not _unset
            else self.answered_question_ids
        )
        new_current_question = (
            current_question
            if current_question is not _unset
            else self.current_question
        )
        return evolve(
            self,
            data=new_data,
            completed=completed if completed is not None else self.completed,
            answered_question_ids=new_question_ids,
            current_question=new_current_question,
        )


def _merge_dict(a: Mapping[str, Any], b: Mapping[str, Any]) -> immutabledict[str, Any]:
    updated = {**a, **b}
    return make_immutable(updated)
