"""Registration module."""

from collections.abc import Sequence

from attrs import frozen
from oes.utils.request import CattrsBody, raise_not_found
from oes.web.interview import InterviewService, get_interview_registrations
from oes.web.registration import Registration, RegistrationService
from oes.web.routes.common import InterviewStateRequestBody, response_converter
from oes.web.types import JSON
from sanic import Blueprint, Forbidden, HTTPResponse, Request, json

routes = Blueprint("registrations")


@frozen
class RegistrationResponse:
    """Registration response."""

    registration: Registration
    summary: str | None


@routes.get("/events/<event_id>/registrations")
@response_converter
async def list_registrations(
    request: Request,
    event_id: str,
    registration_service: RegistrationService,
) -> Sequence[RegistrationResponse]:
    """List registrations."""
    args = request.get_args(keep_blank_values=True)
    q = args.get("q", "") or ""
    account_id = args.get("account_id")
    email = args.get("email")
    results = await registration_service.get_registrations(
        q, event_id=event_id, account_id=account_id, email=email, args=args
    )

    return [
        RegistrationResponse(reg, registration_service.get_registration_summary(reg))
        for reg in results
    ]


@routes.get("/events/<event_id>/registrations/<registration_id>")
@response_converter
async def read_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    registration_service: RegistrationService,
) -> RegistrationResponse:
    """Read a registration."""
    reg = raise_not_found(
        await registration_service.get_registration(event_id, registration_id)
    )
    summary = registration_service.get_registration_summary(reg)
    return RegistrationResponse(reg, summary)


@routes.post(
    "/events/<event_id>/update-registrations",
    name="update_registrations_from_interview",
)
async def update_registrations_from_interview(
    request: Request,
    interview_service: InterviewService,
    registration_service: RegistrationService,
    event_id: str,
    body: CattrsBody,
) -> HTTPResponse:
    """Add a registration from an interview."""
    req_body = await body(InterviewStateRequestBody)
    interview = raise_not_found(
        await interview_service.get_completed_interview(req_body.state)
    )
    if interview.target != request.url:
        raise Forbidden

    registrations = get_interview_registrations(interview)
    access_code = interview.context.get("access_code")

    # TODO: check access code

    access_codes = (
        {r.registration.id: access_code for r in registrations} if access_code else {}
    )

    res_code, res_body = await registration_service.apply_batch_change(
        event_id, (r.registration for r in registrations), access_codes
    )

    if res_code == 409:
        return json(_strip_cart_error(res_body), status=res_code)
    elif res_code == 200:
        return HTTPResponse(status=204)
    else:
        return json(res_body, status=res_code)


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
