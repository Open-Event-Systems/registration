"""Admin routes."""

from attrs import frozen
from oes.utils.request import raise_not_found
from oes.web.config import Config
from oes.web.interview import InterviewService, InterviewState
from oes.web.registration import RegistrationService
from oes.web.routes.common import response_converter
from sanic import Blueprint, Request

routes = Blueprint("admin")


@frozen
class AdminInterviewOption:
    """Admin interview option."""

    url: str
    title: str | None = None


@routes.get(
    "/events/<event_id>/registrations/<registration_id>/admin/change/<interview_id>",
    name="start_admin_change_interview",
)
@response_converter
async def start_admin_change_interview(
    request: Request,
    config: Config,
    event_id: str,
    registration_id: str,
    interview_id: str,
    registration_service: RegistrationService,
    interview_service: InterviewService,
) -> InterviewState:
    """Start an admin change interview."""
    event = raise_not_found(config.events.get(event_id))
    reg = raise_not_found(
        await registration_service.get_registration(event_id, registration_id)
    )
    opt = raise_not_found(
        next(
            (
                o
                for o in registration_service.get_admin_change_options(reg)
                if o.id == interview_id
            ),
            None,
        )
    )
    target_url = request.url_for(
        "registrations.update_registrations_from_interview", event_id=event_id
    )
    context = {
        "event_id": event_id,
        "event": event.get_template_context(),
    }

    data = {
        "registration": dict(reg),
    }

    state = await interview_service.start_interview(
        request.host, opt.id, target_url, context, data
    )
    return state
