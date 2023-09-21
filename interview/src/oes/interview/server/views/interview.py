"""Interview views."""
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Optional, Union

from attrs import Factory, evolve, frozen
from blacksheep import Request, Response, auth
from blacksheep.exceptions import BadRequest
from blacksheep.messages import get_absolute_url_to_path
from blacksheep.server.openapi.v3 import OpenAPIHandler
from loguru import logger
from oes.interview.config.interview import InterviewConfig
from oes.interview.interview.error import InvalidStateError
from oes.interview.interview.interview import Interview
from oes.interview.interview.run import run_interview
from oes.interview.interview.state import InterviewState
from oes.interview.serialization import converter
from oes.interview.server.app import json_response, router
from oes.interview.server.docs import (
    docs,
    docs_helper,
    interview_state_json_schema,
    interview_state_result_schema,
)
from oes.interview.server.request import parse_request
from oes.interview.server.response import JSONStateResponse, make_blob_state_response
from oes.interview.server.settings import Settings
from oes.template import Context
from oes.util.blacksheep import FromAttrs, check_404
from openapidocs.v3 import Encoding, MediaType, Operation, RequestBody
from openapidocs.v3 import Response as OpenAPIResponse
from openapidocs.v3 import Schema, ValueFormat, ValueType


@frozen
class InterviewListItem:
    """An interview list result."""

    id: str
    title: Optional[str]


@frozen(kw_only=True)
class StartInterviewRequest:
    """Request to start an interview."""

    target_url: Optional[str] = None
    submission_id: Optional[str] = None
    expiration_date: Optional[datetime] = None
    context: dict[str, Any] = Factory(dict)
    data: dict[str, Any] = Factory(dict)


@frozen(kw_only=True)
class InterviewResultRequest:
    """Interview result request."""

    state: str


@docs.register(interview_state_result_schema)
@frozen(kw_only=True)
class InterviewResultResponse:
    """Interview result."""

    interview: Interview
    target_url: Optional[str] = None
    submission_id: str
    expiration_date: datetime
    complete: bool
    context: Context
    data: Context


# just for docs


@frozen
class _Question:
    id: str
    title: Optional[str]
    description: Optional[str]
    fields: Sequence[dict]
    when: Union[str, bool, list]


@frozen
class _InterviewSchema:
    id: Optional[str]
    title: Optional[str]
    questions: Sequence[_Question]
    steps: Sequence[dict]


@frozen(kw_only=True)
class _InterviewResultSchema:
    interview: _InterviewSchema
    target_url: Optional[str] = None
    submission_id: str
    expiration_date: datetime
    complete: bool
    context: Context
    data: Context


@auth("authenticated")
@router.get("/interviews")
@docs_helper(
    summary="List interviews",
    response_type=list[InterviewListItem],
    response_summary="The available interviews",
    tags=["Interviews"],
)
async def list_interviews(
    interview_config: InterviewConfig,
    request: Request,
) -> Response:
    """List configured interviews."""
    return json_response(
        [
            InterviewListItem(
                id=str(get_absolute_url_to_path(request, f"/interviews/{id_}")),
                title=i.title,
            )
            for id_, i in interview_config.items()
        ]
    )


@auth("authenticated")
@router.get("/interviews/{interview_id}")
@docs_helper(
    summary="Get an interview config",
    response_type=Interview,
    response_summary="The interview config",
    tags=["Interviews"],
)
async def get_interview(
    interview_id: str,
    request: Request,
    interviews: InterviewConfig,
) -> Response:
    """Get the interview configuration."""
    interview = check_404(interviews.get(interview_id))

    # set ID to the url
    interview = evolve(
        interview,
        id=str(get_absolute_url_to_path(request, f"/interviews/{interview_id}")),
    )

    return json_response(interview)


def _set_start_interview_docs(docs: OpenAPIHandler, op: Operation):
    op.responses = {
        "200": OpenAPIResponse(
            content={
                "application/json": MediaType(
                    schema=interview_state_json_schema,
                    example={
                        "content": {
                            "type": "question",
                            "schema": {
                                "field_0": "...",
                                "field_1": "...",
                            },
                        },
                        "update_url": "http://localhost/update",
                        "state": "Wq4t2aBO8Db97;JWd",
                    },
                ),
                "application/octet-stream": MediaType(
                    schema=Schema(
                        type=ValueType.STRING,
                        format=ValueFormat.BINARY,
                    ),
                ),
            }
        )
    }


@auth("authenticated")
@router.post("/interviews/{interview_id}")
@docs_helper(
    summary="Start an interview",
    tags=["Interviews"],
    on_created=_set_start_interview_docs,
)
async def start_interview(
    interview_id: str,
    body: FromAttrs[StartInterviewRequest],
    request: Request,
    interviews: InterviewConfig,
    settings: Settings,
) -> Response:
    """Start an interview."""
    interview = check_404(interviews.get(interview_id))

    state = InterviewState(
        interview=interview,
        target_url=body.value.target_url,
        submission_id=body.value.submission_id,
        expiration_date=body.value.expiration_date,
        context=body.value.context,
        data=body.value.data,
    )

    accept = request.get_first_header(b"accept")

    # get to the first content
    state, content = await run_interview(state)

    if accept == b"application/octet-stream":
        return make_blob_state_response(
            state,
            content,
            request=request,
            secret=settings.encryption_key.get_secret_value(),
        )
    else:
        return json_response(
            JSONStateResponse.create(
                state,
                content,
                request=request,
                secret=settings.encryption_key.get_secret_value(),
            )
        )


def _set_get_result_docs(docs: OpenAPIHandler, op: Operation):
    op.request_body = RequestBody(
        content={
            "application/json": MediaType(
                schema=Schema(
                    type=ValueType.OBJECT,
                    properties={"state": Schema(type=ValueType.STRING)},
                    required=["state"],
                ),
            ),
            "multipart/form-data": MediaType(
                schema=Schema(
                    type=ValueType.OBJECT,
                    properties={
                        "state": Schema(
                            type=ValueType.STRING, format=ValueFormat.BINARY
                        )
                    },
                    required=["state"],
                ),
                encoding={
                    "state": Encoding("application/octet-stream"),
                },
            ),
        }
    )


@auth("authenticated")
@router.post("/result")
@docs_helper(
    summary="Get an interview result",
    response_type=InterviewResultResponse,
    response_summary="The completed state",
    tags=["Result"],
    on_created=_set_get_result_docs,
)
async def get_result(request: Request, settings: Settings) -> Response:
    """Get an interview result."""

    update_req = await parse_request(request)

    try:
        state = InterviewState.decrypt(
            update_req.state,
            converter=converter,
            secret=settings.encryption_key.get_secret_value(),
        )
        state.validate()
    except InvalidStateError as e:
        logger.debug(f"Invalid state: {e}")
        raise BadRequest

    if not state.complete:
        logger.debug("Invalid state: interview is not complete")
        raise BadRequest

    # Set the interview ID to the URL
    interview = evolve(
        state.interview,
        id=str(get_absolute_url_to_path(request, f"/interviews/{state.interview.id}")),
    )

    return json_response(
        InterviewResultResponse(
            interview=interview,
            target_url=state.target_url,
            submission_id=state.submission_id,
            expiration_date=state.expiration_date,
            complete=state.complete,
            context=state.context,
            data=state.data,
        )
    )
