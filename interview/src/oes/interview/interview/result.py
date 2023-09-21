"""Specific step result content."""
from typing import Literal, Mapping, Optional, Union

from attr import frozen
from typing_extensions import TypeAlias


@frozen(kw_only=True)
class AskResult:
    """A result asking a question."""

    type: Literal["question"] = "question"
    schema: Mapping[str, object]


@frozen(kw_only=True)
class ExitResult:
    """An exit result."""

    type: Literal["exit"] = "exit"
    title: str
    description: Optional[str] = None


ResultContent: TypeAlias = Union[AskResult, ExitResult]
