"""Interview config."""
import itertools
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Optional, Union

from attrs import field, frozen
from cattrs import Converter
from oes.interview.config.file import load_config_file, resolve_config_path
from oes.interview.input.question import Question
from oes.interview.interview.interview import Interview, Step
from oes.interview.util import validate_identifier


class InterviewConfig(Mapping[str, Interview]):
    """Interview configuration."""

    _interviews: dict[str, Interview]

    def __init__(self, interviews: Mapping[str, Interview]):
        self._interviews = dict(interviews)

    def __getitem__(self, key: str) -> Interview:
        return self._interviews[key]

    def __len__(self) -> int:
        return len(self._interviews)

    def __iter__(self) -> Iterator[str]:
        return iter(self._interviews)


@frozen
class InterviewConfigEntry:
    """Interview config entry."""

    id: str = field(validator=validate_identifier)
    """The interview ID."""

    title: Optional[str] = None
    """The interview title."""

    questions: Sequence[Union[Path, Question]] = ()
    """The available questions in the interview."""

    steps: Sequence[Step] = ()
    """The steps."""

    def get_interview(self, converter: Converter) -> Interview:
        """Get an :class:`Interview` object from this config entry."""

        questions = tuple(
            itertools.chain.from_iterable(
                _load_question_or_path(converter, entry) for entry in self.questions
            )
        )

        return Interview(
            id=self.id, title=self.title, questions=questions, steps=self.steps
        )


def load_interviews(
    converter: Converter, config_path: Union[Path, str]
) -> InterviewConfig:
    """Load interviews from a config file."""
    with resolve_config_path(config_path) as path:
        doc = load_config_file(path)

        entries = converter.structure(doc, Sequence[InterviewConfigEntry])

        interviews = {i.id: i.get_interview(converter) for i in entries}

        return InterviewConfig(interviews)


def _load_question_or_path(
    converter: Converter, obj: Union[Path, Question]
) -> Sequence[Question]:
    if isinstance(obj, Path):
        return _load_question_file(converter, obj)
    else:
        return (obj,)


def _load_question_file(converter: Converter, path: Path) -> Sequence[Question]:
    with resolve_config_path(path) as resolved:
        doc = load_config_file(resolved)
        return converter.structure(doc, Sequence[Question])


def structure_question_or_path(
    converter: Converter, v: object, t: object
) -> Union[Question, Path]:
    """Structure a question or path to a questions config."""
    if isinstance(v, (Path, str)):
        return Path(v)
    else:
        return converter.structure(v, Question)
