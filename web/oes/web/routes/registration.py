"""Registration module."""

from collections.abc import Mapping, Sequence

from cattrs.preconf.orjson import make_converter
from oes.utils.request import CattrsBody, raise_not_found
from oes.web.interview2 import InterviewRegistration, InterviewService
from oes.web.registration2 import Registration, RegistrationService
from oes.web.routes.common import InterviewStateRequestBody
from oes.web.types import JSON
from sanic import Blueprint, Forbidden, HTTPResponse, Request, json

routes = Blueprint("registrations")


@routes.post(
    "/events/<event_id>/registrations/add", name="add_registration_from_interview"
)
async def add_registration_from_interview(
    request: Request,
    interview_service: InterviewService,
    registration_service: RegistrationService,
    event_id: str,
    body: CattrsBody,
) -> HTTPResponse:
    """Add a registration from an interview."""
    req_body = await body(InterviewStateRequestBody)
    interview_state = raise_not_found(
        await interview_service.get_completed_interview(req_body.state)
    )
    if interview_state.target != request.url:
        raise Forbidden

    registrations, access_codes = _parse_interview(
        interview_state.context, interview_state.data
    )

    res_code, res_body = await registration_service.apply_batch_change(
        event_id, registrations, access_codes
    )

    if res_code == 409:
        return json(_strip_cart_error(res_body), status=res_code)
    elif res_code == 200:
        return HTTPResponse(status=204)
    else:
        return json(res_body, status=res_code)


_converter = make_converter()


def _parse_interview(
    context: JSON, data: JSON
) -> tuple[Sequence[Registration], Mapping[str, str]]:
    access_code = context.get("access_code")
    reg_data = data.get("registration")
    registration = (
        _converter.structure(reg_data, Registration) if reg_data is not None else None
    )
    registrations = _converter.structure(
        data.get("registrations", []), Sequence[InterviewRegistration]
    )

    all_registrations: list[Registration] = []
    if registration is not None:
        all_registrations.append(registration)
    all_registrations.extend(r.registration for r in registrations)
    access_codes = {r.id: access_code for r in all_registrations} if access_code else {}

    return all_registrations, access_codes


# TODO: dedupe this
def _strip_cart_error(cart_error: JSON) -> JSON:
    """Remove detailed data from the cart conflict response."""
    stripped = {"results": []}
    for res in cart_error.get("results", []):
        stripped["results"].append(
            {
                "change": {"id": res.get("change", {}).get("id")},
                "errors": res.get("errors", []),
            }
        )

    return stripped
