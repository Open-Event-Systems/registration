"""Routes."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Literal, Union, cast

from attrs import field, frozen
from immutabledict import immutabledict
from oes.interview.input.question import ValidationError
from oes.interview.interview.interview import Interview, make_interview_context
from oes.interview.interview.state import InterviewState, ParentInterviewContext
from oes.interview.interview.step_types.ask import AskResult
from oes.interview.interview.step_types.exit import ExitResult
from oes.interview.interview.update import update_interview
from oes.interview.storage import StorageService
from oes.utils.request import BadRequest, CattrsBody, raise_not_found
from oes.utils.response import ResponseConverter
from sanic import Blueprint, HTTPResponse, NotFound, Request
from typing_extensions import TypeAlias

routes = Blueprint("interview")


def _json_default(v):
    if isinstance(v, immutabledict):
        return dict(v)
    else:
        raise TypeError(type(v))


response_converter = ResponseConverter(json_default=_json_default)


@frozen
class InterviewStartRequest:
    """Request body to start an interview."""

    target: str
    context: Mapping[str, Any] = field(factory=dict)
    data: Mapping[str, Any] = field(factory=dict)


@frozen
class InterviewUpdateRequest:
    """Request body to start an interview."""

    state: str
    responses: Mapping[str, Any] | None = None


@frozen
class IncompleteInterviewResponse:
    """Incomplete interview response body."""

    state: str
    completed: Literal[False]
    target: str
    content: AskResult | ExitResult | None = None


@frozen
class CompleteInterviewResponse:
    """Completed response body."""

    state: str
    completed: Literal[True]
    target: str


InterviewResponse: TypeAlias = Union[
    IncompleteInterviewResponse, CompleteInterviewResponse
]
"""Interview response."""


@frozen
class InterviewResultResponse:
    """A completed interview result."""

    date_started: datetime
    date_expires: datetime
    target: str
    context: Mapping[str, Any]
    data: Mapping[str, Any]


@routes.post("/interviews/<interview_id>")
@response_converter
async def start_interview(
    request: Request, storage: StorageService, interview_id: str, body: CattrsBody
) -> InterviewResponse:
    """Start an interview."""
    interviews: Mapping[str, Interview] = request.app.ctx.interviews
    interview = raise_not_found(interviews.get(interview_id))

    req = await body(InterviewStartRequest)

    state = InterviewState(
        target=req.target,
        context=req.context,
        data=req.data,
    )
    context = make_interview_context(
        interview.questions,
        interview.steps,
        state,
        interviews,
    )
    key = await storage.put(context)
    return _make_response(request, key, state, None)


@routes.post("/update-interview", name="update_interview_route")
@response_converter
async def update_interview_route(
    request: Request, storage: StorageService, body: CattrsBody
) -> InterviewResponse:
    """Update an interview."""
    req = await body(InterviewUpdateRequest)
    context = raise_not_found(await storage.get(req.state))

    try:
        result_ctx, content = await update_interview(context, req.responses)
    except ValidationError:
        exc = BadRequest("Invalid input")
        exc.status_code = 422
        raise exc
    key = await storage.put(result_ctx)
    return _make_response(request, key, result_ctx.state, content)


@routes.get("/completed-interviews/<state>")
@response_converter
async def completed_interview_route(
    request: Request, state: str, storage: StorageService
) -> InterviewResultResponse:
    interview = raise_not_found(await storage.get(state))
    if not interview.state.completed:
        raise NotFound

    now = datetime.now().astimezone()
    if now >= interview.state.date_expires:
        raise NotFound

    assert not isinstance(interview.state.target, ParentInterviewContext)

    return InterviewResultResponse(
        date_started=interview.state.date_started,
        date_expires=interview.state.date_expires,
        target=interview.state.target,
        context=interview.state.context,
        data=interview.state.data,
    )


@routes.get("/_healthcheck")
async def healthcheck(request: Request, storage: StorageService) -> HTTPResponse:
    """Health check endpoint."""
    await storage.get("")
    return HTTPResponse(status=204)


def _make_response(
    request: Request, key: str, state: InterviewState, content: object | None
) -> InterviewResponse:
    if state.completed:
        assert isinstance(state.target, str)
        return CompleteInterviewResponse(key, state.completed, state.target)
    else:
        update_url = request.url_for("interview.update_interview_route")
        return IncompleteInterviewResponse(
            key, state.completed, update_url, cast(AskResult, content)
        )
