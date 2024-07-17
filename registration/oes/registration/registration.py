"""Registration module."""

import uuid
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime
from enum import Enum
from typing import Any

from attr import fields
from attrs import define, field
from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from oes.registration.orm import Base
from oes.utils.orm import JSON, Repo
from sqlalchemy import UUID, Index, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


class Status(str, Enum):
    """Registration status values."""

    pending = "pending"
    created = "created"
    canceled = "canceled"


class StatusError(ValueError):
    """Raised when a registration's status is not acceptable."""

    pass


class ConflictError(ValueError):
    """Raised when a registration version conflict occurs."""

    def __init__(self, msg: str = "Version mismatch"):
        super().__init__(msg)


class Registration(Base, kw_only=True):
    """Registration entity."""

    __tablename__ = "registration"
    __table_args__ = (Index("ix_email", text("LOWER(email)")),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, default_factory=lambda: uuid.uuid4(), primary_key=True
    )
    event_id: Mapped[str]
    version: Mapped[int] = mapped_column(default=1)
    status: Mapped[Status] = mapped_column(default=Status.pending)
    date_created: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now().astimezone()
    )
    date_updated: Mapped[datetime | None] = mapped_column(
        default=None, onupdate=lambda: datetime.now().astimezone()
    )
    number: Mapped[int | None] = mapped_column(default=None)
    first_name: Mapped[str | None] = mapped_column(default=None)
    last_name: Mapped[str | None] = mapped_column(default=None)
    email: Mapped[str | None] = mapped_column(default=None)
    account_id: Mapped[str | None] = mapped_column(default=None, index=True)
    extra_data: Mapped[JSON] = mapped_column(default_factory=dict)

    __mapper_args__ = {"version_id_col": version}

    def complete(self) -> bool:
        """Complete the registration."""
        if self.status == Status.pending:
            self.status = Status.created
            return True
        elif self.status == Status.canceled:
            raise StatusError("Registration is already canceled")
        else:
            return False

    def cancel(self) -> bool:
        """Cancel the registration."""
        if self.status != Status.canceled:
            self.status = Status.canceled
            return True
        else:
            return False


_registration_meta_fields = frozenset(
    (
        "id",
        "event_id",
        "version",
        "status",
        "date_created",
        "date_updated",
    )
)


@define(kw_only=True)
class RegistrationDataFields:
    """Registration data fields."""

    number: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    account_id: str | None = None


_registration_data_fields: frozenset[str] = frozenset(
    attr.name for attr in fields(RegistrationDataFields)
)

_registration_fields = _registration_meta_fields | _registration_data_fields


@define(kw_only=True)
class RegistrationCreateFields(RegistrationDataFields):
    """Registration fields settable on creation."""

    status: Status = Status.pending
    extra_data: JSON = field(factory=dict)

    def create(self, event_id: str) -> Registration:
        """Create a :class:`Registration`."""
        kw = {k: getattr(self, k) for k in _registration_data_fields}
        return Registration(
            event_id=event_id, status=self.status, extra_data=self.extra_data, **kw
        )


@define(kw_only=True)
class RegistrationUpdateFields(RegistrationDataFields):
    """Updatable registration fields."""

    version: int | None = None
    extra_data: JSON = field(factory=dict)

    def apply(self, registration: Registration):
        """Apply the attributes to a :class:`Registration`."""
        for k in _registration_data_fields:
            setattr(registration, k, getattr(self, k))
        registration.extra_data = self.extra_data


@define(kw_only=True)
class RegistrationBatchChangeFields(RegistrationDataFields):
    """Fields for batch creation/update."""

    id: uuid.UUID
    event_id: str
    status: Status = Status.pending
    version: int | None = None
    extra_data: JSON = field(factory=dict)

    def apply(self, registration: Registration | None) -> Registration:
        """Create a new :class:`Registration` or update the given existing one."""
        if registration:
            for k in _registration_data_fields:
                setattr(registration, k, getattr(self, k))
            registration.status = self.status
            registration.extra_data = self.extra_data
        else:
            args = {
                "id": self.id,
                "event_id": self.event_id,
                "status": self.status,
                "extra_data": self.extra_data,
                **{k: getattr(self, k) for k in _registration_data_fields},
            }
            registration = Registration(
                **{k: v for k, v in args.items() if v is not None}
            )
        return registration


@define
class RegistrationChangeResult:
    """Holds the result of a registration change."""

    id: uuid.UUID
    """The ID."""

    old: Mapping[str, Any]
    """The old data."""

    registration: Registration
    """The final registration entity."""


class RegistrationRepo(Repo[Registration, str | uuid.UUID]):
    """Registration repository."""

    entity_type = Registration

    async def get(
        self,
        id: str | uuid.UUID,
        *,
        event_id: str | None = None,
        lock: bool = False,
    ) -> Registration | None:
        res = await super().get(id, lock=lock)
        return None if res is None or event_id and res.event_id != event_id else res

    async def get_multi(
        self,
        ids: Iterable[str | uuid.UUID],
        *,
        event_id: str | None = None,
        lock: bool = False,
    ) -> Sequence[Registration]:
        """Get multiple :class:`Registration` entities."""
        ids = tuple(ids)
        if not ids:
            return ()

        q = select(Registration).where(Registration.id.in_(ids))

        if event_id:
            q = q.where(Registration.event_id == event_id)

        if lock:
            q = q.order_by(Registration.id).with_for_update()

        res = await self.session.execute(q)
        return res.scalars().all()

    async def search(
        self,
        *,
        event_id: str,
        account_id: str | None = None,
        email: str | None = None,
    ) -> Sequence[Registration]:
        """Search registrations."""
        q = (
            select(Registration)
            .where(Registration.event_id == event_id)
            .order_by(Registration.date_created.desc())
        )

        or_clauses = []

        if account_id:
            or_clauses.append(Registration.account_id == account_id)

        if email:
            or_clauses.append(func.lower(Registration.email) == email.lower())

        if or_clauses:
            q = q.where(or_(*or_clauses))

        res = await self.session.execute(q)
        return res.scalars().all()


class RegistrationService:
    """Manages registration creation/updates."""

    def __init__(
        self,
        session: AsyncSession,
        repo: RegistrationRepo,
        converter: Converter,
    ):
        self.session = session
        self.repo = repo
        self.converter = converter

    async def create(
        self, event_id: str, data: RegistrationCreateFields
    ) -> RegistrationChangeResult:
        """Create a registration."""
        reg = data.create(event_id)
        self.repo.add(reg)
        return RegistrationChangeResult(reg.id, {}, reg)

    async def update(
        self,
        event_id: str,
        registration_id: uuid.UUID | str,
        data: RegistrationUpdateFields,
        etag: str | None = None,
    ) -> RegistrationChangeResult | None:
        """Update a registration."""
        reg = await self.repo.get(registration_id, event_id=event_id)
        if reg is None:
            return None

        if (
            etag is not None
            and etag != self.get_etag(reg)
            or data.version is not None
            and data.version != reg.version
        ):
            raise ConflictError

        old_data = self.converter.unstructure(reg)

        data.apply(reg)
        return RegistrationChangeResult(reg.id, old_data, reg)

    def get_etag(self, registration: Registration) -> str:
        """Get the ETag for a registration."""
        return f'W/"{registration.version}"'


def make_registration_fields_structure_fn(
    cl: (
        type[Registration]
        | type[RegistrationCreateFields]
        | type[RegistrationUpdateFields]
        | type[RegistrationBatchChangeFields]
    ),
    converter: Converter,
) -> Callable[[Any, Any], Any]:
    """Make a function to structure a registration-like object."""
    dict_fn = make_dict_structure_fn(cl, converter)

    def structure(v: Any, t: Any) -> Any:
        if not isinstance(v, Mapping):
            raise ValueError("Invalid registration")
        extra_data = _get_extra_data(v)
        return dict_fn({**v, "extra_data": extra_data}, t)

    return structure


def make_registration_unstructure_fn(
    converter: Converter,
) -> Callable[[Registration], Any]:
    """Make a function to unstructure a :class:`Registration`."""
    dict_fn = make_dict_unstructure_fn(
        Registration,
        converter,
        _cattrs_omit_if_default=True,
        version=override(omit_if_default=False),
        status=override(omit_if_default=False),
    )

    def unstructure(v: Registration) -> dict[str, Any]:
        data = dict_fn(v)
        extra = data.pop("extra_data", {})
        return {**extra, **data}

    return unstructure


def make_registration_batch_change_unstructure_fn(
    converter: Converter,
) -> Callable[[RegistrationBatchChangeFields], Any]:
    """Make a function to unstructure a :class:`RegistrationBatchChangeFields`."""
    dict_fn = make_dict_unstructure_fn(
        RegistrationBatchChangeFields,
        converter,
        _cattrs_omit_if_default=True,
        version=override(omit_if_default=False),
        status=override(omit_if_default=False),
    )

    def unstructure(v: RegistrationBatchChangeFields) -> dict[str, Any]:
        data = dict_fn(v)
        extra = data.pop("extra_data", {})
        return {**extra, **data}

    return unstructure


def _get_extra_data(data: Mapping[str, Any]) -> dict[str, Any]:
    return dict((k, v) for k, v in data.items() if k not in _registration_fields)
