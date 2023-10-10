"""Result content module."""
from __future__ import annotations

from typing import Union

from oes.interview.interview.step_types.ask import AskResult
from oes.interview.interview.step_types.exit import ExitResult
from typing_extensions import TypeAlias

ResultContent: TypeAlias = Union[AskResult, ExitResult]
"""Step result content type."""
