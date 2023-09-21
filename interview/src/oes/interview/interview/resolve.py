"""Functions for resolving values."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Iterable, Iterator

from oes.interview.input.logic import evaluate_whenable
from oes.interview.input.question import Question
from oes.interview.interview.error import InterviewError
from oes.interview.interview.result import AskResult
from oes.interview.interview.state import InterviewState
from oes.interview.variables.locator import Locator, UndefinedError
from oes.template import Context


def get_ask_result_for_variable(
    state: InterviewState,
    loc: Locator,
) -> tuple[str, AskResult]:
    """Get an :class:`AskResult` providing a value for ``loc``.

    Args:
        state: The :class:`InterviewState`.
        loc: The variable :class:`Locator`.

    Returns:
        A pair of the question ID and an :class:`AskResult`.
    """
    question_id, schema = _get_question_schema_for_variable(state, loc)
    return question_id, AskResult(
        schema=schema,
    )


def _get_question_schema_for_variable(
    state: InterviewState,
    loc: Locator,
) -> tuple[str, Mapping[str, object]]:
    """Get the JSON schema for a question providing a value for ``loc``.

    Args:
        state: The :class:`InterviewState`.
        loc: The variable :class:`Locator`.

    Returns:
        A pair of the question ID and the JSON schema.
    """
    questions_by_id = state.interview.questions_by_id
    return _recursive_get_question_schema_for_variable(questions_by_id, state, loc)


def _recursive_get_question_schema_for_variable(
    questions: Mapping[str, Question],
    state: InterviewState,
    loc: Locator,
) -> tuple[str, Mapping[str, object]]:
    try:
        question = _get_question_for_variable(questions, state, loc)
        schema = question.get_schema(state.template_context)
        return question.id, schema
    except UndefinedError as e:
        return _recursive_get_question_schema_for_variable(questions, state, e.locator)


def _get_question_for_variable(
    questions_by_id: Mapping[str, Question],
    state: InterviewState,
    loc: Locator,
) -> Question:
    ctx = state.template_context
    questions: Iterator[Question] = iter(questions_by_id.values())
    questions = _get_unanswered_questions(questions, state)
    questions = _get_questions_matching_conditions(questions, ctx)
    questions = _get_questions_providing_var(questions, loc, ctx)

    question = next(questions, None)

    if question is None:
        raise InterviewError(f"No question providing {loc}")

    return question


def _get_unanswered_questions(
    questions: Iterable[Question],
    state: InterviewState,
) -> Iterator[Question]:
    for question in questions:
        if question.id not in state.answered_question_ids:
            yield question


def _get_questions_matching_conditions(
    questions: Iterable[Question],
    context: Context,
) -> Iterator[Question]:
    for question in questions:
        if evaluate_whenable(question, context):
            yield question


def _get_questions_providing_var(
    questions: Iterable[Question], loc: Locator, context: Context
) -> Iterator[Question]:
    """Yield :class:`Question` objects that provide the value at ``loc``."""
    for q in questions:
        locs = (f.set for f in q.fields if f.set)
        if any(other.compare(loc, context) for other in locs):
            yield q
