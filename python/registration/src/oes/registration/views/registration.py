"""Registration views."""
import uuid
from collections.abc import Mapping
from typing import Any, Optional, Union
from uuid import UUID

from attrs import Factory, field, frozen
from blacksheep import (
    Content,
    FromJSON,
    FromQuery,
    HTTPException,
    Request,
    Response,
    auth,
    json,
)
from blacksheep.exceptions import BadRequest, Forbidden, NotFound
from blacksheep.messages import get_absolute_url_to_path
from blacksheep.server.openapi.common import (
    ContentInfo,
    ParameterInfo,
    ParameterSource,
    RequestBodyInfo,
    ResponseInfo,
)
from blacksheep.url import build_absolute_url
from cattrs import BaseValidationError
from loguru import logger
from oes.registration.app import app
from oes.registration.auth.handlers import (
    RequireCheckIn,
    RequireRegistration,
    RequireRegistrationEdit,
    RequireRegistrationEditOrAction,
)
from oes.registration.auth.scope import Scope
from oes.registration.auth.user import User
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper, serialize
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.hook.models import HookEvent
from oes.registration.hook.service import HookSender
from oes.registration.interview.service import InterviewService
from oes.registration.log import AuditLogType, audit_log
from oes.registration.models.event import EventConfig, SimpleEventInfo
from oes.registration.models.logic import when_matches
from oes.registration.models.registration import (
    Registration,
    RegistrationState,
    RegistrationUpdatedEvent,
    WritableRegistration,
)
from oes.registration.serialization import get_converter
from oes.registration.services.event import EventService
from oes.registration.services.registration import RegistrationService
from oes.registration.services.registration import (
    check_in_registration as _check_in_registration,
)
from oes.registration.util import check_not_found
from oes.registration.views.responses import (
    BodyValidationError,
    InterviewOption,
    RegistrationListResponse,
)
from oes.util import get_now
from oes.util.blacksheep import Conflict


@frozen(kw_only=True)
class CreateRegistrationRequest:
    """Request body to create a registration."""

    state: RegistrationState = RegistrationState.created
    event_id: str
    number: Optional[int] = None
    option_ids: set[str] = field(default=Factory(lambda: set()))
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None


@frozen(kw_only=True)
class UpdateRegistrationRequest:
    """Request body to update a registration."""

    number: Optional[int] = None
    option_ids: set[str] = field(default=Factory(lambda: set()))
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None


@auth(RequireRegistration)
@app.router.get("/registrations")
@docs_helper(
    response_type=list[RegistrationListResponse],
    response_summary="The list of registrations",
    tags=["Registration"],
    skip_serialize=True,
)
@transaction
async def list_registrations(
    reg: RegistrationService,
    q: Optional[str] = None,
    event_id: Optional[str] = None,
    after: Optional[UUID] = None,
    all: bool = False,
) -> Response:
    """Search registrations."""
    results = await reg.list_registrations(q, event_id=event_id, after=after, all=all)

    converter = get_converter()
    response = json(
        [
            converter.unstructure(
                RegistrationListResponse.from_registration(r.get_model())
            )
            for r in results
        ]
    )

    return response


@auth(RequireRegistrationEdit)
@app.router.get("/registrations/interviews")
@docs_helper(
    response_type=list[InterviewOption],
    response_summary="The interview options",
    tags=["Registration"],
)
async def list_registration_add_interviews(
    event_id: FromQuery[str],
    events: EventConfig,
    user: User,
    interview_service: InterviewService,
) -> list[InterviewOption]:
    """List interviews to create registrations."""
    event = check_not_found(events.get_event(event_id.value))
    context = {
        "user": {
            "id": str(user.id),
            "email": user.email,
        }
    }

    titles = await _get_interview_titles(interview_service)

    options = []
    for interview in event.admin_add_interviews:
        if when_matches(interview, context):
            options.append(
                InterviewOption(
                    interview.id, _get_interview_title(titles, interview.id)
                )
            )

    return options


@auth(RequireRegistrationEdit)
@app.router.get("/registrations/new-interview")
@docs(
    responses={
        200: ResponseInfo(
            "The interview state response",
        ),
    },
    tags=["Registration"],
)
async def get_registration_create_interview(
    request: Request,
    event_id: FromQuery[str],
    interview_id: FromQuery[str],
    events: EventConfig,
    user: User,
    interview_service: InterviewService,
) -> Mapping[str, Any]:
    """Get an interview state to create a new registration."""
    event = check_not_found(events.get_event(event_id.value))
    interview = check_not_found(
        next(
            (i for i in event.admin_add_interviews if i.id == interview_id.value), None
        )
    )

    context = {
        "user": {
            "id": str(user.id),
            "email": user.email,
        }
    }
    if not when_matches(interview, context):
        raise NotFound

    model = Registration(
        id=uuid.uuid4(),
        state=RegistrationState.pending,
        event_id=event_id.value,
        version=1,
        date_created=get_now(),
    )

    registration_data = get_converter().unstructure(model)

    context = {
        "event": get_converter().unstructure(SimpleEventInfo.create(event)),
        # cart interviews have this in data... maybe needs to be moved?
        "meta": {
            "account_id": str(user.id),
            "email": user.email,
        },
    }

    initial_data = {"registration": registration_data}

    target_url = get_absolute_url_to_path(request, "/registrations")

    state = await interview_service.start_interview(
        interview_id.value,
        target_url=target_url.value.decode(),
        context=context,
        initial_data=initial_data,
    )
    return state


@auth(RequireRegistrationEdit)
@app.router.post("/registrations")
@docs(
    responses={
        200: ResponseInfo(
            "The created response",
        )
    },
    tags=["Registration"],
)
@transaction
async def create_registration(
    request: Request,
    body: FromJSON[dict[str, Any]],
    registration_service: RegistrationService,
    interview_service: InterviewService,
    event_service: EventService,
    event_config: EventConfig,
) -> Response:
    """Create a registration."""
    if len(body.value) == 1 and "state" in body.value:
        created = await _create_registration_from_interview(
            body.value["state"],
            request,
            registration_service,
            interview_service,
            event_config,
            event_service,
        )
    else:
        created = await _create_registration_direct(
            body.value, registration_service, event_config, event_service
        )

    return registration_response(created)


async def _create_registration_direct(
    body: dict[str, Any],
    service: RegistrationService,
    event_config: EventConfig,
    event_service: EventService,
) -> Registration:
    """Create a registration."""
    event = event_config.get_event(body.get("event_id", ""))
    if not event:
        raise HTTPException(422, "Event ID not found")

    data = _parse_registration_data(
        {
            "state": RegistrationState.pending.value,
            **body,
            "id": uuid.uuid4(),
            "version": 1,
        }
    )

    event_stats = await event_service.get_event_stats(event.id, lock=True)

    entity = RegistrationEntity(
        id=data.id,
        state=data.state,
        event_id=event.id,
        number=data.number,
        option_ids=list(data.option_ids),
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        preferred_name=data.preferred_name,
        extra_data=data.extra_data,
    )

    await service.create_registration(entity, event_stats)

    return entity.get_model()


async def _create_registration_from_interview(
    state: str,
    request: Request,
    service: RegistrationService,
    interview_service: InterviewService,
    event_config: EventConfig,
    event_service: EventService,
) -> Registration:
    current_url = build_absolute_url(
        request.scheme.encode(),
        request.host.encode(),
        request.base_path.encode(),
        request.url.path,
    ).value.decode()

    interview_result = await interview_service.get_result(state, target_url=current_url)
    if not interview_result:
        logger.debug("Interview result is not valid")
        raise BadRequest

    reg = _parse_registration_data(interview_result.data.get("registration", {}))

    event = event_config.get_event(reg.event_id)
    if not event:
        raise HTTPException(422, "Event ID not found")

    event_stats = await event_service.get_event_stats(event.id, lock=True)

    entity = RegistrationEntity(
        state=reg.state,
        event_id=event.id,
        number=reg.number,
        option_ids=list(reg.option_ids),
        email=reg.email,
        first_name=reg.first_name,
        last_name=reg.last_name,
        preferred_name=reg.preferred_name,
        extra_data=reg.extra_data,
    )

    await service.create_registration(entity, event_stats)

    return entity.get_model()


@auth(RequireRegistration)
@app.router.get("/registrations/{id}")
@docs(
    responses={
        200: ResponseInfo(
            "The registration",
            content=[ContentInfo(Registration)],
        )
    },
    tags=["Registration"],
)
async def read_registration(
    id: UUID,
    service: RegistrationService,
) -> Response:
    """Read a registration."""
    reg = check_not_found(await service.get_registration(id))

    return registration_response(reg.get_model())


@auth(RequireRegistrationEditOrAction)
@app.router.get("/registrations/{id}/interviews")
@docs_helper(
    response_type=list[InterviewOption],
    response_summary="The available interviews.",
    tags=["Registration"],
)
async def list_registration_change_interviews(
    id: UUID,
    registration_service: RegistrationService,
    interview_service: InterviewService,
    events: EventConfig,
    user: User,
) -> list[InterviewOption]:
    """List registration change interviews."""
    reg = check_not_found(await registration_service.get_registration(id))
    event = events.get_event(reg.event_id)

    if not event:
        return []

    context = {
        "user": {
            "id": str(user.id),
            "email": user.email,
        },
        "registration": get_converter().unstructure(reg.get_model()),
    }

    titles = await _get_interview_titles(interview_service)

    options = []
    for interview in event.admin_change_interviews:
        if when_matches(interview, context):
            options.append(
                InterviewOption(
                    interview.id, _get_interview_title(titles, interview.id)
                )
            )

    return options


@auth(RequireRegistrationEditOrAction)
@app.router.get("/registrations/{id}/new-interview")
@docs(
    responses={
        200: ResponseInfo(
            "The interview state response",
        ),
    },
    tags=["Registration"],
)
async def get_registration_change_interview(
    id: UUID,
    request: Request,
    interview_id: FromQuery[str],
    events: EventConfig,
    user: User,
    interview_service: InterviewService,
    registration_service: RegistrationService,
) -> Mapping[str, Any]:
    """Get an interview state to change a registration."""
    reg = check_not_found(await registration_service.get_registration(id))
    event = check_not_found(events.get_event(reg.event_id))

    interview = check_not_found(
        next(
            (i for i in event.admin_change_interviews if i.id == interview_id.value),
            None,
        )
    )

    reg_model = reg.get_model()

    context = {
        "user": {
            "id": str(user.id),
            "email": user.email,
        },
        "registration": get_converter().unstructure(reg_model),
    }
    if not when_matches(interview, context):
        raise NotFound

    context = {
        "event": get_converter().unstructure(SimpleEventInfo.create(event)),
        # cart interviews have this in data... maybe needs to be moved?
        "meta": {
            "account_id": str(user.id),
            "email": user.email,
        },
    }

    initial_data = {
        "registration": get_converter().unstructure(reg.get_model()),
    }

    if not when_matches(interview, context):
        raise NotFound

    target_url = get_absolute_url_to_path(request, f"/registrations/{id}")

    state = await interview_service.start_interview(
        interview_id.value,
        target_url=target_url.value.decode(),
        context=context,
        initial_data=initial_data,
    )
    return state


async def _get_interview_titles(service: InterviewService) -> dict[str, Optional[str]]:
    interviews = await service.get_interviews()
    return {i.id: i.title for i in interviews}


def _get_interview_title(titles: dict[str, Optional[str]], id: str) -> str:
    title = titles.get(id)
    if not title:
        _, _, title = id.rpartition("/")
    return title


@auth(RequireRegistrationEditOrAction)
@app.router.put("/registrations/{id}")
@docs(
    parameters={
        "If-Match": ParameterInfo(
            "The ETag of the current version of the registration",
            value_type=str,
            source=ParameterSource.HEADER,
            required=True,
            example='W/"asdf1234"',
        )
    },
    request_body=RequestBodyInfo(
        description="The new data or interview state",
        examples={
            "Direct update": {
                "first_name": "NewFirst",
                "last_name": "NewLast",
                "number": 123,
                "nickname": "Nickname",
            },
            "Interview state": {"state": "<interview state>"},
        },
    ),
    responses={
        200: ResponseInfo(
            "The updated registration",
            content=[ContentInfo(Registration)],
        )
    },
    tags=["Registration"],
)
@transaction
async def update_registration(
    request: Request,
    id: UUID,
    service: RegistrationService,
    hook_sender: HookSender,
    body: FromJSON[dict[str, Any]],
    user: User,
    interview_service: InterviewService,
) -> Response:
    """Update a registration."""
    reg = check_not_found(await service.get_registration(id, lock=True))

    old_data = reg.get_model()

    if (
        len(body.value) == 1
        and "state" in body.value
        and (
            user.has_scope(Scope.registration_action)
            or user.has_scope(Scope.registration_edit)
        )
    ):
        new_data = await _update_registration_from_interview(
            body.value["state"], request, reg, interview_service
        )
    elif user.has_scope(Scope.registration_edit):
        new_data = _update_registration_from_request(request, reg, body.value)
    else:
        raise Forbidden

    await hook_sender.schedule_hooks_for_event(
        HookEvent.registration_updated,
        RegistrationUpdatedEvent(
            old_data=old_data,
            new_data=new_data,
        ),
    )

    audit_log.bind(type=AuditLogType.registration_update).success(
        "Registration {registration} updated", registration=reg
    )

    return registration_response(reg.get_model())


def _update_registration_from_request(
    request: Request,
    registration: RegistrationEntity,
    body: dict[str, Any],
) -> Registration:
    check_etag(request, registration)

    # should already be loaded
    writable = get_converter().structure(body, WritableRegistration)
    registration.update_properties_from_model(writable)
    new_data = registration.get_model()
    return new_data


async def _update_registration_from_interview(
    state: str,
    request: Request,
    registration: RegistrationEntity,
    interview_service: InterviewService,
) -> Registration:
    current_url = build_absolute_url(
        request.scheme.encode(),
        request.host.encode(),
        request.base_path.encode(),
        request.url.path,
    ).value.decode()
    interview_result = await interview_service.get_result(state, target_url=current_url)
    if not interview_result:
        logger.debug("Interview result is not valid")
        raise HTTPException(409)

    new_reg_data = _parse_registration_data(
        interview_result.data.get("registration", {})
    )
    if new_reg_data.version != registration.version:
        raise HTTPException(409)

    registration.update_properties_from_model(new_reg_data)
    return registration.get_model()


def _parse_registration_update_data(data: dict[str, Any]) -> WritableRegistration:
    try:
        reg = get_converter().structure(data, WritableRegistration)
    except BaseValidationError as e:
        raise BodyValidationError(e)
    return reg


def _parse_registration_data(data: dict[str, Any]) -> Registration:
    try:
        registration = get_converter().structure(data, Registration)
    except BaseValidationError as e:
        raise BodyValidationError(e)
    return registration


@auth(RequireRegistrationEdit)
@app.router.put("/registrations/{id}/complete")
@docs(
    responses={
        200: ResponseInfo(
            "The updated registration",
            content=[ContentInfo(Registration)],
        )
    },
    tags=["Registration"],
)
@transaction
async def complete_registration(
    id: UUID,
    service: RegistrationService,
    hook_sender: HookSender,
    event_service: EventService,
) -> Response:
    """Complete a pending registration."""
    reg = check_not_found(await service.get_registration(id, lock=True))

    # TODO: permissions

    try:
        stats = await event_service.get_event_stats(reg.event_id, lock=True)
        reg.complete() and await hook_sender.schedule_hooks_for_event(
            HookEvent.registration_created, reg.get_model()
        )
        reg.assign_number(stats)
    except ValueError as e:
        raise HTTPException(409, str(e))

    return registration_response(reg.get_model())


@auth(RequireRegistrationEdit)
@app.router.put("/registrations/{id}/cancel")
@docs(
    responses={
        200: ResponseInfo(
            "The updated registration",
            content=[ContentInfo(Registration)],
        )
    },
    tags=["Registration"],
)
@transaction
async def cancel_registration(
    id: UUID,
    service: RegistrationService,
    hook_sender: HookSender,
) -> Response:
    """Cancel a pending registration."""
    reg = check_not_found(await service.get_registration(id, lock=True))

    # TODO: permissions

    try:
        reg.cancel() and await hook_sender.schedule_hooks_for_event(
            HookEvent.registration_canceled,
            reg.get_model(),
        )
    except ValueError as e:
        raise HTTPException(409, str(e))

    return registration_response(reg.get_model())


@auth(RequireCheckIn)
@app.router.get("/registrations/{id}/check-in")
@docs(
    responses={
        200: ResponseInfo(
            "An interview state response",
        )
    },
    tags=["Registration"],
)
@serialize(dict[str, Any])
async def read_check_in_interview(
    id: UUID,
    station_id: FromQuery[Optional[str]],
    request: Request,
    service: RegistrationService,
    interview_service: InterviewService,
    events: EventConfig,
) -> dict[str, Any]:
    """Get a check-in interview state for a registration."""
    registration = check_not_found(await service.get_registration(id))

    event = events.get_event(registration.event_id)
    if not event:
        # event config isn't available
        raise NotFound

    interview_id = event.check_in_interview
    target_url = get_absolute_url_to_path(request, f"/registrations/{id}/check-in")

    context = {
        "station_id": station_id.value,
        "registration": get_converter().unstructure(registration.get_model()),
    }

    response = await interview_service.start_interview(
        interview_id,
        target_url=target_url.value.decode(),
        context=context,
    )
    return response


@auth(RequireCheckIn)
@app.router.post("/registrations/{id}/check-in")
@docs(
    request_body=RequestBodyInfo(
        "The interview state from the check-in interview.",
        examples={
            "Example": {
                "state": "...",
            }
        },
    ),
    responses={204: ResponseInfo("The check-in was completed")},
    tags=["Registration"],
)
@transaction
async def check_in_registration(
    id: UUID,
    request: Request,
    body: FromJSON[dict[str, Any]],
    service: RegistrationService,
    interview_service: InterviewService,
    user: User,
) -> Response:
    """Check-in a registration."""
    registration = check_not_found(
        await service.get_registration(id, lock=True, include_check_ins=True)
    )

    state = body.value.get("state")
    if not state:
        raise BadRequest

    current_url = build_absolute_url(
        request.scheme.encode(),
        request.host.encode(),
        request.base_path.encode(),
        request.url.path,
    ).value.decode()

    interview_result = await interview_service.get_result(state, target_url=current_url)
    if not interview_result:
        logger.debug("Interview result is not valid")
        raise BadRequest

    current_ver = interview_result.context["registration"]["version"]
    if current_ver != registration.version:
        raise Conflict("Registration has been updated during check-in")

    _check_in_registration(registration, user, interview_result.data)

    return Response(204)


# TODO: determine delete semantics


def check_etag(request: Request, reg: Union[Registration, RegistrationEntity]):
    """Check that the ETag matches, or raise :class:`HTTPException`."""
    header = request.headers.get_first(b"If-Match")
    if not header:
        raise HTTPException(428)  # precondition required

    expected = get_etag(reg)
    if header != expected:
        raise HTTPException(412)  # precondition failed


def registration_response(reg: Registration) -> Response:
    """Return a JSON-encode :class:`Registration`.

    Sets the ``ETag`` header.
    """
    data = get_converter().dumps(reg)
    etag = get_etag(reg)
    return Response(
        200,
        headers=[
            (b"ETag", etag),
        ],
        content=Content(
            b"application/json",
            data,
        ),
    )


def get_etag(reg: Union[Registration, RegistrationEntity]) -> bytes:
    """Get the ETag for a registration's version."""
    return f'W/"{reg.version}"'.encode()
