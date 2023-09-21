"""Response types."""
import base64
from typing import Optional

from attrs import frozen
from blacksheep import Content, Request, Response
from blacksheep.messages import get_absolute_url_to_path
from oes.interview.interview.error import InvalidInputError
from oes.interview.interview.result import ResultContent
from oes.interview.interview.state import InterviewState
from oes.interview.serialization import converter, json_default
from typing_extensions import Self


@frozen
class JSONStateResponse:
    """JSON state response."""

    state: str
    content: Optional[ResultContent] = None
    complete: Optional[bool] = None
    update_url: Optional[str] = None
    target_url: Optional[str] = None

    @classmethod
    def create(
        cls,
        state: InterviewState,
        content: Optional[ResultContent] = None,
        /,
        *,
        request: Request,
        secret: bytes,
    ) -> Self:
        """Create a JSON state response."""

        enc = state.encrypt(secret=secret, converter=converter, default=json_default)
        state_str = base64.b85encode(enc)

        return cls(
            state_str.decode(),
            content,
            complete=state.complete,
            update_url=str(get_absolute_url_to_path(request, "/update"))
            if not state.complete
            else None,
            target_url=state.target_url if state.complete else None,
        )


@frozen
class BlobResponseData:
    """Blob response data."""

    content: Optional[ResultContent] = None
    complete: Optional[bool] = None
    update_url: Optional[str] = None
    target_url: Optional[str] = None


def make_blob_state_response(
    state: InterviewState,
    content: Optional[ResultContent] = None,
    /,
    *,
    request: Request,
    secret: bytes,
) -> Response:
    """Return result and state in one binary blob response."""
    response_data = BlobResponseData(
        content=content,
        complete=state.complete,
        update_url=str(get_absolute_url_to_path(request, "/update"))
        if not state.complete
        else None,
        target_url=state.target_url if state.complete else None,
    )
    json_bytes = converter.dumps(response_data, default=json_default)

    state_bytes = state.encrypt(
        secret=secret, converter=converter, default=json_default
    )

    return Response(
        200,
        content=Content(
            b"application/octet-stream", json_bytes + b"\r\n\r\n" + state_bytes
        ),
    )


def get_error_response(input_error: InvalidInputError) -> Response:
    """Get a response for a validation error."""
    return Response(
        422,
        content=Content(
            b"application/json",
            converter.dumps({"errors": input_error.details}),
        ),
    )
