"""Functions to update interviews."""
from __future__ import annotations

# TODO name
from collections.abc import Callable
from typing import TYPE_CHECKING, Iterable, Mapping, Optional, Union

from attrs import define, field, frozen
from cattrs import BaseValidationError, Converter
from httpx import AsyncClient
from oes.interview.input import ResponseParser, UserResponse
from oes.interview.interview import InterviewError, InvalidInputError
from oes.interview.interview.resolve import get_ask_result_for_variable
from oes.interview.interview.state import InterviewState
from oes.interview.interview.types import Step
from oes.interview.logic import UndefinedError, evaluate_whenable
from typing_extensions import Literal

if TYPE_CHECKING:
    from oes.interview.interview import ResultContent


MAX_UPDATE_COUNT = 100
"""The maximum number of updates that can happen in a single update."""


def _default_converter() -> Converter:
    from oes.interview.serialization import converter

    return converter


def _default_json() -> Callable[[object], object]:
    from oes.interview.serialization import json_default

    return json_default


@define
class InterviewUpdate:
    """Holds information about the interview update process."""

    state: InterviewState
    """The interview state."""

    http_client: AsyncClient
    """The HTTP client to use."""

    converter: Converter = field(factory=_default_converter)
    """The :class:`Converter` to use to serialize data."""

    json_default: Callable[[object], object] = field(factory=_default_json)
    """The JSON default function to use."""

    step_count: int = 0
    """The number of steps handled."""


@frozen
class StepResult:
    """The result of a step."""

    state: InterviewState
    """The updated :class:`InterviewState`."""

    changed: bool
    """Whether the interview state was changed."""

    content: Optional[ResultContent] = None
    """Result content."""


async def update_interview(
    update: InterviewUpdate,
    response: Optional[Mapping[str, object]] = None,
) -> Optional[ResultContent]:
    """Update the interview state.

    Updates values in ``update``.

    Args:
        update: The :class:`InterviewUpdate` object.
        response: The submitted response.

    Returns:
        The result content.
    """
    if update.state.question_id is not None:
        update.state = _apply_response(update.state, response)

    try:
        return await _run_interview_steps(update)
    except UndefinedError as e:
        if e.pointer is None:
            raise e
        # look up a question to resolve the undefined variable
        question_id, ask_result = get_ask_result_for_variable(update.state, e.pointer)
        update.state = update.state.set_question(question_id)

        return ask_result


async def handle_steps(update: InterviewUpdate, steps: Iterable[Step]) -> StepResult:
    """Handle interview steps.

    Args:
        update: The :class:`InterviewUpdate` object.
        steps: The steps.

    Returns:
        The :class:`StepResult`.
    """
    ctx = update.state.template_context
    for step in steps:
        if evaluate_whenable(step, ctx):
            result = await step(update)
            if result.changed:
                return result

    return StepResult(update.state, changed=False)


def _apply_response(
    state: InterviewState,
    response: Optional[UserResponse],
) -> InterviewState:
    """Validate and apply a user response if a question was asked."""
    if state.question_id is not None:
        question = state.interview.get_question(state.question_id)
        if not question:
            raise InterviewError(f"Question ID not found: {state.question_id}")

        # Apply response and unset question ID
        state = _validate_and_apply_response(state, question.response_parser, response)

        # Unset question ID
        return state.set_question(None)
    else:
        return state


def _validate_and_apply_response(
    state: InterviewState,
    parser: ResponseParser,
    response: Optional[UserResponse],
) -> InterviewState:
    try:
        values = parser(response or {})
    except BaseValidationError as e:
        raise InvalidInputError(e) from e

    try:
        return state.set_values(values)
    except UndefinedError as e:
        raise InterviewError(
            f"Undefined value {e.pointer!r} when setting {values!r}. "
            "Collections are not automatically created."
        )


async def _run_interview_steps(
    update: InterviewUpdate,
) -> Optional[ResultContent]:
    """Run the steps, returning result content or a completed interview.

    Updates values in ``update``.
    """
    changed = True
    content = None

    while content is None and changed:
        if update.step_count >= MAX_UPDATE_COUNT:
            raise InterviewError("Too many state updates")
        changed, content = await _run_once(update)
        update.step_count += 1

    return content


async def _run_once(
    update: InterviewUpdate,
) -> Union[tuple[Literal[True], Optional[ResultContent]], tuple[Literal[False], None]]:
    """Handle the interview steps and update values in ``update``.

    Returns:
        A pair of a bool indicating whether a change was made, and result content.
    """
    result = await handle_steps(update, update.state.interview.steps)  # noqa: NEW100
    if result.changed:
        update.state = result.state
        return True, result.content
    else:
        # if all steps ran without any changes/content, the interview is complete
        update.state = update.state.set_complete()
        return False, None
