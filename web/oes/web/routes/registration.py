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
class RegistrationAddOption:
    """Registration add option."""

    title: str
    url: str


@frozen
class RegistrationChangeOption:
    """Registration change option."""

    title: str
    auto: bool
    url: str


@frozen
class RegistrationResponse:
    """Registration response."""

    registration: Registration
    summary: str | None = None
    display_data: Sequence[tuple[str, str]] = ()
    change_options: Sequence[RegistrationChangeOption] = ()


@frozen
class RegistrationListResponse:
    """Registration list response."""

    registrations: Sequence[RegistrationResponse]
    add_options: Sequence[RegistrationAddOption] = ()


@routes.get("/events/<event_id>/registrations")
@response_converter
async def list_registrations(
    request: Request,
    event_id: str,
    registration_service: RegistrationService,
) -> RegistrationListResponse:
    """List registrations."""
    user_role = request.headers.get("x-role")
    args = request.get_args(keep_blank_values=True)
    q = args.get("q", "") or ""
    account_id = args.get("account_id")
    email = args.get("email")
    summary = args.get("summary")
    results = await registration_service.get_registrations(
        q, event_id=event_id, account_id=account_id, email=email, args=args
    )

    registrations = [
        RegistrationResponse(
            reg, registration_service.get_registration_summary(reg) if summary else None
        )
        for reg in results
    ]

    add_opts = registration_service.get_admin_add_options(event_id, user_role)

    return RegistrationListResponse(
        registrations,
        tuple(
            RegistrationAddOption(
                o.title,
                request.url_for(
                    "admin.start_admin_add_interview",
                    event_id=event_id,
                    interview_id=o.id,
                ),
            )
            for o in add_opts
        ),
    )


@routes.get("/events/<event_id>/registrations/<registration_id>")
async def read_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    registration_service: RegistrationService,
) -> HTTPResponse:
    """Read a registration."""
    reg, etag = await registration_service.get_registration_with_etag(
        event_id, registration_id
    )
    reg = raise_not_found(reg)

    reg_body = response_converter.converter.unstructure(
        _make_registration_response(request, reg, registration_service)
    )
    headers = {"ETag": etag} if etag else {}
    return json(reg_body, headers=headers)


@routes.put("/events/<event_id>/registrations/<registration_id>")
async def update_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    registration_service: RegistrationService,
) -> HTTPResponse:
    """Update a registration."""
    body = request.json
    if_match = request.headers.get("If-Match")
    status, resp, etag = await registration_service.proxy_registration_request(
        "PUT", f"/events/{event_id}/registrations/{registration_id}", body, if_match
    )
    if resp is None:
        return HTTPResponse(status=status)
    elif status != 200:
        return json(resp, status)
    else:
        reg = Registration(resp["registration"])
        reg_body = response_converter.converter.unstructure(
            _make_registration_response(request, reg, registration_service)
        )
        headers = {"ETag": etag} if etag else {}
        return json(reg_body, headers=headers)


@routes.put("/events/<event_id>/registrations/<registration_id>/complete")
async def complete_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    registration_service: RegistrationService,
) -> HTTPResponse:
    """Complete a registration."""
    status, resp, etag = await registration_service.proxy_registration_request(
        "PUT", f"/events/{event_id}/registrations/{registration_id}/complete"
    )
    if resp is None:
        return HTTPResponse(status=status)
    elif status != 200:
        return json(resp, status)
    else:
        reg = Registration(resp["registration"])
        reg_body = response_converter.converter.unstructure(
            _make_registration_response(request, reg, registration_service)
        )
        headers = {"ETag": etag} if etag else {}
        return json(reg_body, headers=headers)


@routes.put("/events/<event_id>/registrations/<registration_id>/cancel")
async def cancel_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    registration_service: RegistrationService,
) -> HTTPResponse:
    """Complete a registration."""
    status, resp, etag = await registration_service.proxy_registration_request(
        "PUT", f"/events/{event_id}/registrations/{registration_id}/cancel"
    )
    if resp is None:
        return HTTPResponse(status=status)
    elif status != 200:
        return json(resp, status)
    else:
        reg = Registration(resp["registration"])
        reg_body = response_converter.converter.unstructure(
            _make_registration_response(request, reg, registration_service)
        )
        headers = {"ETag": etag} if etag else {}
        return json(reg_body, headers=headers)


@routes.put("/events/<event_id>/registrations/<registration_id>/assign-number")
async def assign_number_to_registration(
    request: Request,
    event_id: str,
    registration_id: str,
    registration_service: RegistrationService,
) -> HTTPResponse:
    """Complete a registration."""
    status, resp, etag = await registration_service.proxy_registration_request(
        "PUT", f"/events/{event_id}/registrations/{registration_id}/assign-number"
    )
    if resp is None:
        return HTTPResponse(status=status)
    elif status != 200:
        return json(resp, status)
    else:
        reg = Registration(resp["registration"])
        reg_body = response_converter.converter.unstructure(
            _make_registration_response(request, reg, registration_service)
        )
        headers = {"ETag": etag} if etag else {}
        return json(reg_body, headers=headers)


def _make_registration_response(
    request: Request, reg: Registration, registration_service: RegistrationService
):
    user_role = request.headers.get("x-role")
    summary = registration_service.get_registration_summary(reg)
    display_data = registration_service.get_display_data(reg)
    change_options = registration_service.get_admin_change_options(reg, user_role)
    return RegistrationResponse(
        reg,
        summary,
        display_data,
        [
            RegistrationChangeOption(
                c.title,
                c.auto,
                request.url_for(
                    "admin.start_admin_change_interview",
                    event_id=reg.event_id,
                    registration_id=reg.id,
                    interview_id=c.id,
                ),
            )
            for c in change_options
        ],
    )


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
    scope = [s.strip() for s in request.headers.get("x-scope", "").split(",")]
    req_body = await body(InterviewStateRequestBody)
    interview = raise_not_found(
        await interview_service.get_completed_interview(req_body.state)
    )
    if interview.target != request.url:
        raise Forbidden

    registrations = get_interview_registrations(interview)
    access_code = interview.context.get("access_code")

    access_codes = (
        {r.registration.id: access_code for r in registrations} if access_code else {}
    )

    res_code, res_body = await registration_service.apply_batch_change(
        event_id, (r.registration for r in registrations), access_codes
    )

    if res_code == 409:
        return json(_strip_cart_error(res_body), status=res_code)
    elif res_code == 200:
        if "registration" in scope:
            return json(res_body, status=res_code)
        else:
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
