"""Interview types."""
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

from attrs import frozen
from oes.interview.input.types import Whenable
from typing_extensions import Protocol

if TYPE_CHECKING:
    from cattrs import Converter
    from httpx import AsyncClient
    from oes.interview.interview.interview import StepResult
    from oes.interview.interview.state import InterviewState


@frozen
class StepConfig:
    """Step configuration object."""

    converter: Converter
    """The :class:`Converter` to use to serialize data."""

    json_default: Callable[[object], object]
    """The JSON default function to use."""

    http_client: AsyncClient
    """The HTTP client to use."""


class Step(Whenable, Protocol):
    """A step in an interview."""

    @abstractmethod
    async def __call__(
        self, state: InterviewState, config: StepConfig, /
    ) -> StepResult:
        """Handle the step."""
        ...
