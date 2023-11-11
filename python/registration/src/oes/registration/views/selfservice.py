"""Self-service views."""
from typing import Optional

from blacksheep import FromQuery, auth
from oes.registration.access_code.models import AccessCodeSettings
from oes.registration.access_code.service import AccessCodeService
from oes.registration.app import app
from oes.registration.auth.handlers import RequireSelfService
from oes.registration.auth.user import User
from oes.registration.docs import docs_helper
from oes.registration.interview.service import InterviewService
from oes.registration.models.event import EventConfig
from oes.registration.services.registration import (
    RegistrationService,
    get_allowed_add_interviews,
    get_allowed_change_interviews,
    render_self_service_registration,
)
from oes.registration.util import check_not_found
from oes.registration.views.responses import (
    InterviewOption,
    SelfServiceRegistrationListResponse,
    SelfServiceRegistrationResponse,
)


@auth(RequireSelfService)
@app.router.get("/self-service/registrations")
@docs_helper(
    response_type=SelfServiceRegistrationListResponse,
    response_summary="The list of self service registrations",
    tags=["Self-Service"],
)
async def list_self_service_registration(
    event_id: FromQuery[Optional[str]],
    access_code: FromQuery[Optional[str]],
    service: RegistrationService,
    event_config: EventConfig,
    user: User,
    interview_service: InterviewService,
    access_code_service: AccessCodeService,
) -> SelfServiceRegistrationListResponse:
    """List self-service registrations."""
    access_code_settings = await _get_access_code(
        access_code.value, event_id.value, access_code_service
    )

    if event_id.value:
        event = check_not_found(event_config.get_event(event_id.value))
        add_options = get_allowed_add_interviews(event, access_code_settings)
    else:
        add_options = []

    registrations = (
        (
            await service.list_self_service_registrations(
                user.id,
                event_id=event_id.value,
                email=user.email,
                access_code_settings=access_code_settings,
            )
        )
        if user.id
        else []
    )

    results = []
    titles = await _get_interview_titles(interview_service)

    for reg in registrations:
        event = event_config.get_event(reg.event_id)
        if event and event.is_visible_to(user):
            change_options = get_allowed_change_interviews(
                event, reg, access_code_settings
            )
            model = render_self_service_registration(event, reg)
            results.append(
                SelfServiceRegistrationResponse(
                    model,
                    [
                        InterviewOption(o.id, _get_interview_title(titles, o.id))
                        for o in change_options
                    ],
                )
            )

    return SelfServiceRegistrationListResponse(
        results,
        [
            InterviewOption(o.id, _get_interview_title(titles, o.id))
            for o in add_options
        ],
    )


async def _get_interview_titles(service: InterviewService) -> dict[str, Optional[str]]:
    interviews = await service.get_interviews()
    return {i.id: i.title for i in interviews}


def _get_interview_title(titles: dict[str, Optional[str]], id: str) -> str:
    title = titles.get(id)
    if not title:
        _, _, title = id.rpartition("/")
    return title


async def _get_access_code(
    code: Optional[str],
    event_id: Optional[str],
    service: AccessCodeService,
) -> Optional[AccessCodeSettings]:
    if not event_id:
        return None

    if code:
        entity = await service.get_access_code(code)
        if entity and entity.event_id == event_id and entity.check_valid():
            return entity.get_settings()
    return None
