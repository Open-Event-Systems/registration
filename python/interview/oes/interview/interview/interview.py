"""Interview module."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Mapping, Optional

from attrs import Factory, field, frozen
from oes.interview.input import Question
from oes.interview.interview.types import Step


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

    def get_question(self, id: str, /) -> Optional[Question]:
        """Get a question by ID."""
        return self._questions_by_id.get(id)


def _make_questions_by_id(interview: Interview) -> Mapping[str, Question]:
    return {q.id: q for q in interview.questions}
