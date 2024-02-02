"""Response types."""

from __future__ import annotations

import base64

from attrs import frozen
from blacksheep import Content, Request, Response
from blacksheep.messages import get_absolute_url_to_path
from oes.interview.interview import InterviewState, InvalidInputError
from oes.interview.serialization import converter, json_default
from typing_extensions import Self


@frozen
class JSONStateResponse:
    """JSON state response."""

    state: str
    content: AskResult | ExitResult | None = None
    complete: bool | None = None
    update_url: str | None = None
    target_url: str | None = None

    @classmethod
    def create(
        cls,
        state: InterviewState,
        content: AskResult | ExitResult | None = None,
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
            update_url=(
                str(get_absolute_url_to_path(request, "/update"))
                if not state.complete
                else None
            ),
            target_url=state.target_url if state.complete else None,
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


# avoid circular references
from oes.interview.interview.step_types.ask import AskResult  # noqa
from oes.interview.interview.step_types.exit import ExitResult  # noqa
