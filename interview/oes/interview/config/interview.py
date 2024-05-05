"""Interview config."""

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from attrs import field, frozen
from cattrs import Converter
from oes.interview.input.question import QuestionTemplate
from oes.interview.interview.types import Step
from ruamel.yaml import YAML

_yaml = YAML(typ="safe")


@frozen(kw_only=True)
class QuestionTemplateObject(QuestionTemplate):
    """A question template as an object."""

    id: str
    """The question ID."""


@frozen
class InterviewConfig:
    """Interview config entry."""

    questions: Sequence[Path | QuestionTemplateObject] = field(
        default=(), converter=tuple[Path | QuestionTemplateObject, ...]
    )
    """The questions to include."""

    steps: Sequence[Step] = field(default=(), converter=tuple[Step, ...])
    """The interview steps."""

    def get_questions(
        self, base_path: Path, converter: Converter
    ) -> Mapping[str, QuestionTemplate]:
        """Get questions for this interview."""
        questions = {}
        for entry in self.questions:
            if isinstance(entry, QuestionTemplateObject):
                questions[entry.id] = QuestionTemplate(
                    entry.title, entry.description, entry.fields, entry.when
                )
            else:
                path = base_path / entry
                questions.update(self._load_questions_from_file(converter, path))
        return questions

    def _load_questions_from_file(
        self, converter: Converter, file: Path
    ) -> Mapping[str, QuestionTemplate]:
        with file.open() as f:
            doc = _yaml.load(f)
        questions = converter.structure(doc, Mapping[str, QuestionTemplate])
        return questions


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


def make_question_template_structure_fn(
    converter: Converter,
) -> Callable[[Any, Any], Any]:
    """Make a function to structure question template objects."""

    def structure(v, t):
        if isinstance(v, (str, Path)):
            return converter.structure(v, Path)
        else:
            return converter.structure(v, QuestionTemplateObject)

    return structure
