"""Routes module."""

import asyncio
from collections.abc import Iterable, Sequence
from datetime import datetime

from attrs import frozen
from oes.checkin.checkin import CheckIn, CheckInRepo, CheckInService
from oes.checkin.config import Config, InterviewOption
from oes.checkin.interview import InterviewService
from oes.checkin.registration import Registration, RegistrationService
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody, raise_not_found
from oes.utils.response import ResponseConverter
from sanic import Blueprint, Forbidden, HTTPResponse, NotFound, Request, json
from sanic.exceptions import HTTPException
from typing_extensions import Self

routes = Blueprint("checkin")
response_converter = ResponseConverter()


class Conflict(HTTPException):
    """HTTP conflict."""

    status_code = 409
    quiet = True


@frozen
class CheckInInterviewOption:
    """Interview option."""

    url: str
    title: str


@frozen
class CheckInListResponse:
    """Check-in list response."""

    id: str
    event_id: str
    session_id: str | None
    date_started: datetime

    @classmethod
    def from_checkin(cls, checkin: CheckIn) -> Self:
        """Create from entity."""
        return cls(
            checkin.id,
            checkin.event_id,
            checkin.session_id,
            checkin.date_started,
        )


@frozen
class CheckInCreateRequest:
    """Check-in create request body."""

    session_id: str | None = None


@frozen
class CheckInResponse:
    """Check-in response."""

    id: str
    event_id: str
    session_id: str | None
    date_started: datetime
    options: Sequence[CheckInInterviewOption]

    @classmethod
    def from_checkin(
        cls, request: Request, checkin: CheckIn, options: Iterable[InterviewOption]
    ) -> Self:
        """Create from entity."""
        return cls(
            checkin.id,
            checkin.event_id,
            checkin.session_id,
            checkin.date_started,
            tuple(
                CheckInInterviewOption(
                    request.url_for(
                        "checkin.start_action",
                        event_id=checkin.event_id,
                        id=checkin.id,
                        action_id=opt.id,
                    ),
                    opt.title,
                )
                for opt in options
            ),
        )


@frozen
class UpdateBody:
    """Update request body."""

    state: str


@routes.get("/events/<event_id>/check-in/sessions")
@response_converter
async def list_checkins(
    request: Request,
    event_id: str,
    repo: CheckInRepo,
) -> Sequence[CheckInListResponse]:
    """List active check-ins."""
    res = await repo.list_active(event_id)
    items = [CheckInListResponse.from_checkin(c) for c in res]
    return items


@routes.get("/events/<event_id>/check-in/sessions/<session_id>")
@response_converter
async def get_checkin_by_session_id(
    request: Request,
    event_id: str,
    session_id: str,
    config: Config,
    repo: CheckInRepo,
    registration_service: RegistrationService,
) -> CheckInResponse:
    """Get a check-in by session ID."""
    event = raise_not_found(config.events.get(event_id))
    res = raise_not_found(await repo.get_by_session_id(event_id, session_id))
    registration = (
        await registration_service.get_registration(event_id, res.registration_id)
        if res.registration_id
        else None
    )
    options = (
        event.get_allowed_actions(registration) if registration is not None else []
    )
    return CheckInResponse.from_checkin(request, res, options)


@routes.get("/events/<event_id>/check-in/by-id/<id>")
@response_converter
async def get_checkin_by_id(
    request: Request,
    event_id: str,
    id: str,
    config: Config,
    repo: CheckInRepo,
    registration_service: RegistrationService,
) -> CheckInResponse:
    """Get a check-in by ID."""
    event = raise_not_found(config.events.get(event_id))
    res = await repo.get(id)
    if not res or res.event_id != event_id:
        raise NotFound

    registration = (
        await registration_service.get_registration(event_id, res.registration_id)
        if res.registration_id
        else None
    )
    options = (
        event.get_allowed_actions(registration) if registration is not None else []
    )
    return CheckInResponse.from_checkin(request, res, options)


@routes.post("/events/<event_id>/check-in/sessions")
@response_converter
@transaction
async def create_checkin(
    request: Request,
    event_id: str,
    body: CattrsBody,
    repo: CheckInRepo,
    service: CheckInService,
    config: Config,
) -> CheckInResponse:
    req_body = await body(CheckInCreateRequest)
    raise_not_found(config.events.get(event_id))
    session_id = req_body.session_id.strip().upper() if req_body.session_id else None
    cur = await repo.get_by_session_id(event_id, session_id) if session_id else None
    print("Cur", session_id, "is", cur)
    if cur:
        raise Conflict
    checkin = service.create(event_id, session_id, None)
    return CheckInResponse.from_checkin(request, checkin, [])


@routes.put("/events/<event_id>/check-in/by-id/<id>/set-registration")
@response_converter
@transaction
async def set_registration_id(
    request: Request,
    event_id: str,
    id: str,
    registration_id: str,
    config: Config,
    repo: CheckInRepo,
    registration_service: RegistrationService,
) -> CheckInResponse:
    """Set the registration for a check-in."""
    event = raise_not_found(config.events.get(event_id))
    res = await repo.get(id)
    if not res or res.event_id != event_id:
        raise NotFound

    registration = raise_not_found(
        await registration_service.get_registration(event_id, registration_id)
    )

    if res.registration_id and res.registration_id != registration_id:
        raise Conflict

    res.registration_id = registration_id
    options = event.get_allowed_actions(registration)
    return CheckInResponse.from_checkin(request, res, options)


@routes.put("/events/<event_id>/check-in/by-id/<id>/close")
@transaction
async def close_checkin(
    request: Request,
    event_id: str,
    id: str,
    config: Config,
    repo: CheckInRepo,
) -> HTTPResponse:
    """Set the registration for a check-in."""
    raise_not_found(config.events.get(event_id))
    res = await repo.get(id)
    if not res or res.event_id != event_id:
        raise NotFound

    if res.date_finished is None:
        res.date_finished = datetime.now().astimezone()
        res.session_id = None
    return HTTPResponse(status=204)


@routes.get(
    "/events/<event_id>/check-in/by-id/<id>/actions/<action_id>", name="start_action"
)
async def start_action(
    request: Request,
    event_id: str,
    id: str,
    action_id: str,
    config: Config,
    repo: CheckInRepo,
    registration_service: RegistrationService,
    interview_service: InterviewService,
) -> HTTPResponse:
    """Start an action."""
    event = raise_not_found(config.events.get(event_id))
    res = await repo.get(id)
    if not res or res.event_id != event_id:
        raise NotFound

    if not res.registration_id:
        raise Conflict

    registration = raise_not_found(
        await registration_service.get_registration(event_id, res.registration_id)
    )

    if not any(o.id == action_id for o in event.get_allowed_actions(registration)):
        raise NotFound

    state = await interview_service.start_interview(
        request.host, "TODO", registration, res.session_id, action_id
    )

    return json(state)


@routes.post("/events/<event_id>/check-in/by-id/<id>/update", name="update_checkin")
async def update_checkin(
    request: Request,
    event_id: str,
    id: str,
    config: Config,
    repo: CheckInRepo,
    registration_service: RegistrationService,
    interview_service: InterviewService,
    body: CattrsBody,
) -> HTTPResponse:
    """Start an action."""
    res_body = await body(UpdateBody)
    raise_not_found(config.events.get(event_id))

    interview = await interview_service.get_completed_interview(res_body.state)
    if not interview or interview.target != request.url:
        raise Forbidden

    res = await repo.get(id)
    if not res or res.event_id != event_id:
        raise NotFound

    if not res.registration_id:
        raise Conflict

    registration = Registration(interview.data.get("registration", {}))

    status, resp_body = await registration_service.apply_change(registration)
    # TODO: redact body?
    return json(resp_body, status=status)
