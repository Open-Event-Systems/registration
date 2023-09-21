"""Functions for processing an interview."""
from typing import Any, Mapping, Optional

from attr import evolve
from cattrs import BaseValidationError
from oes.interview.input.types import ResponseParser
from oes.interview.interview.error import InterviewError, InvalidInputError
from oes.interview.interview.resolve import _get_question_schema_for_variable
from oes.interview.interview.result import AskResult, ResultContent
from oes.interview.interview.state import InterviewState
from oes.interview.interview.step import handle_steps
from oes.interview.variables.locator import UndefinedError


async def run_interview(
    state: InterviewState,
    responses: Optional[Mapping[str, object]] = None,
) -> tuple[InterviewState, Optional[ResultContent]]:
    """Run the interview logic.

    Args:
        state: The interview state.
        responses: The submitted responses.

    Returns:
        A pair of the updated state and response content.
    """

    if state.question_id is not None:
        state = _apply_responses(state, responses)

    try:
        return await _run_interview_steps(state)
    except UndefinedError as e:
        # get a question
        question_id, schema = _get_question_schema_for_variable(state, e.locator)
        state = state.set_question(question_id)

        return state, AskResult(schema=schema)


def _apply_responses(
    state: InterviewState,
    responses: Optional[Mapping[str, Any]],
) -> InterviewState:
    """Validate and apply responses if a question was asked."""
    if state.question_id is not None:
        question = state.interview.questions_by_id.get(state.question_id)
        if not question:
            raise InterviewError(f"Question ID not found: {state.question_id}")

        # Apply responses and unset question ID
        state = _validate_and_apply_responses(
            state, question.response_parser, responses
        )

        # Unset question ID
        return state.set_question(None)
    else:
        return state


def _validate_and_apply_responses(
    state: InterviewState,
    parser: ResponseParser,
    responses: Optional[Mapping[str, Any]],
) -> InterviewState:
    try:
        values = parser(responses or {})
    except BaseValidationError as e:
        raise InvalidInputError(e) from e

    try:
        return state.set_values(values)
    except UndefinedError as e:
        raise InterviewError(
            f"Undefined variable {e.locator!r} when setting {values!r}. "
            "Collections are not automatically created."
        )


async def _run_interview_steps(
    state: InterviewState,
) -> tuple[InterviewState, Optional[ResultContent]]:
    """Run the steps, returning content or a completed interview."""

    continue_ = True
    content = None
    while continue_:
        continue_, state, content = await _run_once(state)

    return state, content


async def _run_once(
    state: InterviewState,
) -> tuple[bool, InterviewState, Optional[ResultContent]]:
    result = await handle_steps(state, state.interview.steps)
    if result.changed:
        # return if there is content, otherwise just re-start with the new state
        if result.content is not None:
            return False, result.state, result.content
        else:
            return True, result.state, None
    else:
        # if all steps ran without any changes/content, the interview is complete
        completed = evolve(
            state,
            complete=True,
        )
        return False, completed, None
