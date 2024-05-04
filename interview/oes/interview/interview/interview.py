"""Interview module."""

from collections.abc import Iterable, Mapping, Sequence

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.types import Step


@frozen
class Interview:
    """An interview."""

    questions: Mapping[str, QuestionTemplate] = field(
        default=immutabledict(), converter=lambda v: immutabledict(v)
    )
    steps: Sequence[Step] = field(default=(), converter=lambda v: tuple(v))


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


def _make_question_id(idx: int) -> str:
    return f"q{idx}"
