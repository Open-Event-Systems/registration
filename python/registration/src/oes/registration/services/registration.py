"""Registration service."""
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any, Optional, Union
from uuid import UUID

from oes.registration.access_code.models import AccessCodeInterview, AccessCodeSettings
from oes.registration.auth.account_service import AccountService
from oes.registration.auth.entities import AccountEntity
from oes.registration.auth.user import User
from oes.registration.entities.event_stats import EventStatsEntity
from oes.registration.entities.registration import (
    RegistrationCheckInEntity,
    RegistrationEntity,
)
from oes.registration.hook.models import HookEvent
from oes.registration.hook.service import HookSender
from oes.registration.log import AuditLogType, audit_log
from oes.registration.models.config import Config
from oes.registration.models.event import Event, EventInterviewOption
from oes.registration.models.logic import when_matches
from oes.registration.models.registration import (
    RegistrationState,
    SelfServiceRegistration,
)
from oes.registration.serialization import get_converter
from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload


class RegistrationService:
    """Registration service."""

    def __init__(self, db: AsyncSession, hook_sender: HookSender, config: Config):
        self.db = db
        self.hook_sender = hook_sender
        self.config = config

    async def create_registration(
        self, registration: RegistrationEntity, event_stats: EventStatsEntity
    ):
        """Create a new registration entity."""
        self.db.add(registration)
        await self.db.flush()
        registration._updated = True  # no need for additional version increases

        if registration.state == RegistrationState.created:
            audit_log.bind(type=AuditLogType.registration_create).success(
                "Registration {registration} created", registration=registration
            )

            registration.assign_number(event_stats)

            await self.hook_sender.schedule_hooks_for_event(
                HookEvent.registration_created,
                registration.get_model(),
            )
        elif registration.state == RegistrationState.pending:
            audit_log.bind(type=AuditLogType.registration_create_pending).success(
                "Registration {registration} created in pending state",
                registration=registration,
            )

            await self.hook_sender.schedule_hooks_for_event(
                HookEvent.registration_pending,
                registration.get_model(),
            )

    async def get_registration(
        self,
        id: UUID,
        *,
        lock: bool = False,
        include_accounts: bool = False,
        include_check_ins: bool = False,
    ) -> Optional[RegistrationEntity]:
        """Get a :class:`RegistrationEntity` by ID.

        Args:
            id: The registration ID.
            lock: Whether to lock the row.
            include_accounts: Include related :class:`AccountEntity` rows.
            include_check_ins: Include related :class:`RegistrationCheckInEntity` rows.
        """
        opts = []

        if include_accounts:
            opts.append(selectinload(RegistrationEntity.accounts))

        if include_check_ins:
            opts.append(selectinload(RegistrationEntity.check_ins))

        return await self.db.get(
            RegistrationEntity, id, with_for_update=lock, options=opts
        )

    async def get_registrations(
        self, ids: Iterable[UUID], *, lock: bool = False
    ) -> Sequence[RegistrationEntity]:
        """Get multiple registrations by ID.

        Args:
            ids: The IDs.
            lock: Whether to lock the rows.
        """
        q = (
            select(RegistrationEntity)
            .where(RegistrationEntity.id.in_(list(ids)))
            .order_by(RegistrationEntity.id)
        )

        if lock:
            q = q.with_for_update()

        res = await self.db.execute(q)
        return res.scalars().all()

    async def list_registrations(
        self,
        query: Optional[str] = None,
        /,
        *,
        event_id: Optional[str] = None,
        after: Optional[UUID] = None,
        all: bool = False,
    ) -> Sequence[RegistrationEntity]:
        """Search for :class:`RegistrationEntity`."""
        q = select(RegistrationEntity)

        if query:
            q = q.where(or_(*_build_search_params(query.strip())))

        if event_id:
            q = q.where(RegistrationEntity.event_id == event_id)

        if not all:
            q = q.where(RegistrationEntity.state == RegistrationState.created)

        if after is not None:
            q = q.where(RegistrationEntity.id > after)

        q = q.order_by(RegistrationEntity.id).limit(50)

        res = await self.db.execute(q)
        return res.scalars().all()

    async def list_self_service_registrations(
        self,
        account_id: UUID,
        event_id: Optional[str] = None,
        email: Optional[str] = None,
        access_code_settings: Optional[AccessCodeSettings] = None,
    ) -> Sequence[RegistrationEntity]:
        """List self-service registrations."""
        if access_code_settings and access_code_settings.registration_id:
            return await self._get_access_code_registration(
                access_code_settings.registration_id
            )
        else:
            return await self._list_self_service_registrations(
                account_id, event_id, email
            )

    async def _list_self_service_registrations(
        self,
        account_id: UUID,
        event_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Sequence[RegistrationEntity]:
        q = select(RegistrationEntity).outerjoin(RegistrationEntity.accounts)

        if email is not None:
            q = q.where(
                or_(
                    func.lower(RegistrationEntity.email) == email.lower(),
                    AccountEntity.id == account_id,
                )
            )
        else:
            q = q.where(AccountEntity.id == account_id)

        if event_id is not None:
            q = q.where(RegistrationEntity.event_id == event_id)

        q = q.where(RegistrationEntity.state == RegistrationState.created)

        q = q.order_by(RegistrationEntity.date_created)

        q = q.options(contains_eager(RegistrationEntity.accounts))
        res = await self.db.execute(q)
        return res.unique().scalars().all()

    async def _get_access_code_registration(
        self, registration_id: UUID
    ) -> Sequence[RegistrationEntity]:
        q = select(RegistrationEntity).outerjoin(RegistrationEntity.accounts)
        q = q.where(RegistrationEntity.id == registration_id)
        q = q.options(contains_eager(RegistrationEntity.accounts))
        res = await self.db.execute(q)
        return res.unique().scalars().all()


def render_self_service_registration(
    event: Event, registration: RegistrationEntity
) -> SelfServiceRegistration:
    """Get a :class:`SelfServiceRegistration` model from an entity."""
    model = registration.get_model()
    event_dict = get_converter().unstructure(event)
    registration_dict = get_converter().unstructure(model)

    context = {
        "event": event_dict,
        "registration": {
            "display_name": registration.display_name,
            **registration_dict,
        },
    }

    result = SelfServiceRegistration(
        id=model.id,
        title=event.display_options.registration.title.render(context),
        subtitle=event.display_options.registration.subtitle.render(context),
        description=event.display_options.registration.description.render(context),
    )

    return result


def get_allowed_add_interviews(
    event: Event,
    access_code: Optional[AccessCodeSettings] = None,
) -> list[Union[EventInterviewOption, AccessCodeInterview]]:
    """Get the add interviews allowed for a registration."""
    if access_code is not None:
        return list(access_code.interviews)

    event_dict = get_converter().unstructure(event)

    context = {
        "event": event_dict,
    }

    return [
        interview
        for interview in event.add_interviews
        if when_matches(interview, context)
    ]


def get_allowed_change_interviews(
    event: Event,
    registration: RegistrationEntity,
    access_code: Optional[AccessCodeSettings] = None,
) -> list[Union[EventInterviewOption, AccessCodeInterview]]:
    """Get the change interviews allowed for a registration."""
    if access_code is not None:
        if (
            access_code.registration_id is None
            or access_code.registration_id == registration.id
        ):
            return list(access_code.change_interviews)
        else:
            return []

    model = registration.get_model()
    event_dict = get_converter().unstructure(event)
    registration_dict = get_converter().unstructure(model)

    context = {
        "event": event_dict,
        "registration": {
            "display_name": registration.display_name,
            **registration_dict,
        },
    }

    return [
        interview
        for interview in event.change_interviews
        if when_matches(interview, context)
    ]


def assign_registration_numbers(
    event_stats: EventStatsEntity, registrations: Iterable[RegistrationEntity]
):
    """Assign registration numbers.

    Skips registrations that are not in the ``created`` state.

    Args:
        event_stats: The :class:`EventStatsEntity` tracking the next number.
        registrations: The registrations to update.
    """
    for reg in registrations:
        if reg.event_id != event_stats.id:
            raise ValueError("Event ID does not match")
        if reg.state == RegistrationState.created:
            reg.assign_number(event_stats)


async def add_account_to_registration(
    account_id: UUID,
    registration: RegistrationEntity,
    account_service: AccountService,
):
    """Associate an account with a registration."""
    account = await account_service.get_account(account_id)
    if account:
        registration.accounts.append(account)


def check_in_registration(
    registration: RegistrationEntity,
    user: Optional[User] = None,
    data: Optional[Mapping[str, Any]] = None,
) -> RegistrationCheckInEntity:
    """Check in a registration.

    Returns:
        The created check-in entity.
    """
    check_in = RegistrationCheckInEntity.create(registration, data=data, user=user)
    registration.check_ins.append(check_in)
    registration.checked_in += 1
    return check_in


def _build_search_params(q: str) -> Iterator[ColumnElement]:
    yield from _get_name_search_clause(q)
    yield from _get_email_search_clause(q)
    yield from _get_number_search_clause(q)


def _get_name_search_clause(q: str) -> Iterator[ColumnElement]:
    fname, _, lname = q.lower().partition(" ")
    fname = fname.strip()
    lname = lname.strip()
    name = fname or lname

    if fname and lname:
        # "first last" or "last first"
        yield and_(
            or_(
                func.lower(RegistrationEntity.preferred_name).startswith(fname),
                func.lower(RegistrationEntity.first_name).startswith(fname),
            ),
            func.lower(RegistrationEntity.last_name).startswith(lname),
        )
        yield and_(
            or_(
                func.lower(RegistrationEntity.preferred_name).startswith(lname),
                func.lower(RegistrationEntity.first_name).startswith(lname),
            ),
            func.lower(RegistrationEntity.last_name).startswith(fname),
        )
    elif name:
        yield func.lower(RegistrationEntity.preferred_name).startswith(name)
        yield func.lower(RegistrationEntity.first_name).startswith(name)
        yield func.lower(RegistrationEntity.last_name).startswith(name)


def _get_email_search_clause(q: str) -> Iterator[ColumnElement]:
    if " " not in q:
        yield func.lower(RegistrationEntity.email).startswith(q.lower())


def _get_number_search_clause(q: str) -> Iterator[ColumnElement]:
    try:
        num = int(q)
        yield RegistrationEntity.number == num
    except ValueError:
        return
