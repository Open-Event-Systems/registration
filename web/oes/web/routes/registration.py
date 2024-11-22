"""Registration module."""

from attrs import frozen
from oes.utils.request import CattrsBody, raise_not_found
from oes.web.config import Config
from oes.web.interview import InterviewService, get_interview_registrations
from oes.web.registration import Registration, RegistrationService
from oes.web.routes.common import InterviewStateRequestBody, response_converter
from oes.web.types import JSON
from sanic import Blueprint, Forbidden, HTTPResponse, Request, json

routes = Blueprint("registrations")


@frozen
class RegistrationCheckInResponse:
    """By check-in ID response."""

    registration: Registration
    check_in_status: str | None


@frozen
class RegistrationSummaryResponse:
    """Registration summary."""

    summary: str | None


@routes.get("/events/<event_id>/registrations/<registration_id>/summary")
@response_converter
async def read_registration_summary(
    request: Request,
    event_id: str,
    registration_id: str,
    config: Config,
    registration_service: RegistrationService,
) -> RegistrationSummaryResponse:
    """Read a registration summary."""
    event = raise_not_found(config.events.get(event_id))
    reg = raise_not_found(
        await registration_service.get_registration(event_id, registration_id)
    )
    # TODO: user info?
    ctx = {"event": event.get_template_context(), "registration": dict(reg)}
    summary = (
        event.admin.registration_summary.render(ctx)
        if event.admin.registration_summary
        else None
    )
    return RegistrationSummaryResponse(summary)


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
