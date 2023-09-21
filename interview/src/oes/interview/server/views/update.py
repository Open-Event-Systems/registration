"""App module."""
from typing import Literal, Optional

from attrs import frozen
from blacksheep import HTTPException, Request, Response, allow_anonymous
from blacksheep.server.openapi.v3 import OpenAPIHandler
from loguru import logger
from oes.interview.interview.error import InvalidInputError
from oes.interview.interview.result import ResultContent
from oes.interview.interview.run import run_interview
from oes.interview.server.app import json_response, router
from oes.interview.server.docs import (
    docs,
    interview_state_json_schema,
    update_form_data_schema,
    update_json_schema,
)
from oes.interview.server.request import parse_request, validate_state
from oes.interview.server.response import (
    JSONStateResponse,
    get_error_response,
    make_blob_state_response,
)
from oes.interview.server.settings import Settings
from openapidocs.v3 import Encoding, Example, MediaType, Operation, RequestBody
from openapidocs.v3 import Response as OpenAPIResponse
from openapidocs.v3 import Schema, ValueFormat, ValueType


@frozen
class IncompleteInterviewStateResponse:
    """A response containing an interview state."""

    update_url: str
    """The update URL."""

    content: Optional[ResultContent]
    """The response content."""


@frozen
class CompleteInterviewStateResponse:
    """A response containing a completed interview state."""

    target_url: str
    """The target URL."""

    complete: Literal[True] = True
    """Whether the state is complete."""


def _set_docs(docs: OpenAPIHandler, op: Operation):
    op.request_body = RequestBody(
        content={
            "application/json": MediaType(
                schema=update_json_schema,
            ),
            "multipart/form-data": MediaType(
                schema=update_form_data_schema,
                encoding={
                    "responses": Encoding(
                        content_type="application/json",
                    ),
                    "state": Encoding(
                        content_type="application/octet-stream",
                    ),
                },
            ),
        }
    )

    op.responses = {
        "200": OpenAPIResponse(
            content={
                "application/json": MediaType(
                    schema=interview_state_json_schema,
                    examples={
                        "Incomplete": Example(
                            value={
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
                        "Complete": Example(
                            value={
                                "complete": True,
                                "target_url": "http://localhost/something",
                                "state": "Wq4t2aBO8Db97;JWd",
                            }
                        ),
                    },
                ),
                "application/octet-stream": MediaType(
                    schema=Schema(type=ValueType.STRING, format=ValueFormat.BINARY),
                ),
            }
        )
    }

    op.security = []


@allow_anonymous()
@router.post("/update")
@docs(
    summary="Update an interview state",
    tags=["Interview"],
    on_created=_set_docs,
)
async def update(
    request: Request,
    settings: Settings,
) -> Response:
    """Submit a state and responses and receive an updated state."""
    update_request = await parse_request(request)
    state = validate_state(update_request.state, settings)

    if state.complete:
        logger.debug("Interview is already complete")
        raise HTTPException(422, "Interview is already complete")

    accept = request.get_first_header(b"accept")

    try:
        state, content = await run_interview(state, responses=update_request.responses)
    except InvalidInputError as e:
        logger.debug(f"Invalid responses: {e}")
        return get_error_response(e)

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
