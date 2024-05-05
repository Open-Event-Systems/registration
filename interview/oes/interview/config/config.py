"""Config module."""

from collections.abc import Generator, Mapping, Sequence
from pathlib import Path

from attrs import field, frozen
from cattrs import Converter
from oes.interview.config.interview import InterviewConfig, InterviewConfigObject
from oes.interview.interview.interview import Interview
from oes.interview.serialization import converter
from ruamel.yaml import YAML

_yaml = YAML(typ="safe")


@frozen
class Config:
    """Config object."""

    interviews: Sequence[Path | InterviewConfigObject] = field(
        default=(), converter=tuple[Path | InterviewConfigObject, ...]
    )

    def get_interviews(
        self, base_dir: Path, converter: Converter = converter
    ) -> Mapping[str, Interview]:
        """Get the interviews from this config."""
        res = {}
        for entry in self.interviews:
            if isinstance(entry, InterviewConfigObject):
                questions = entry.get_questions(base_dir, converter)
                res[entry.id] = Interview(questions, entry.steps)
            else:
                path = base_dir / entry
                res.update(dict(self._load_interviews_from_path(converter, path)))
        return res

    def _load_interviews_from_path(
        self, converter: Converter, path: Path
    ) -> Generator[tuple[str, Interview], None, None]:
        if path.is_dir():
            yield from self._load_interviews_from_directory(converter, path)
        else:
            yield self._load_interview_from_file(converter, path)

    def _load_interviews_from_directory(
        self, converter: Converter, path: Path
    ) -> Generator[tuple[str, Interview], None, None]:
        for entry in path.iterdir():
            name = entry.parts[-1]
            if entry.is_file() and (name.endswith(".yml") or name.endswith(".yaml")):
                yield self._load_interview_from_file(converter, entry)

    def _load_interview_from_file(
        self, converter: Converter, fn: Path
    ) -> tuple[str, Interview]:
        id, _, _ = fn.parts[-1].rpartition(".")
        with fn.open() as f:
            doc = _yaml.load(f)
        config = converter.structure(doc, InterviewConfig)
        questions = config.get_questions(fn.parent, converter)
        return id, Interview(questions, config.steps)


def load_config(path: Path | str, converter: Converter = converter) -> Config:
    """Load the configuration."""
    with Path(path).open("r") as f:
        doc = _yaml.load(f)
    return converter.structure(doc, Config)
