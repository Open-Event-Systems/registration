"""Response types."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime  # noqa
from typing import Any, Optional
from uuid import UUID

from attrs import Factory, frozen
from cattrs import BaseValidationError
from oes.registration.access_code.entities import AccessCodeEntity
from oes.registration.access_code.models import AccessCodeSettings
from oes.registration.cart.models import (
    LineItem,
    Modifier,
    PricingResult,
    PricingResultRegistration,
)
from oes.registration.models.registration import (
    RegistrationState,
    SelfServiceRegistration,
)
from typing_extensions import Self


@frozen(kw_only=True)
class ExceptionDetails:
    """Exception details object."""

    exception: Optional[str] = None
    detail: Optional[str] = None
    children: Optional[list[ExceptionDetails]] = None

    @classmethod
    def _format_validation_error(cls, exc: BaseValidationError) -> ExceptionDetails:
        return cls(
            exception=type(exc).__qualname__,
            detail=exc.message,
            children=(
                [cls._format_exception(sub) for sub in exc.exceptions]
                if len(exc.exceptions) > 0
                else None
            ),
        )

    @classmethod
    def _format_exception(cls, exc: Exception) -> ExceptionDetails:
        if isinstance(exc, BaseValidationError):
            return cls._format_validation_error(exc)
        else:
            if len(exc.args) > 0 and isinstance(exc.args[0], str):
                detail = exc.args[0]
            else:
                detail = None
            type_ = type(exc).__qualname__
            return cls(exception=type_, detail=detail)

    @classmethod
    def create(cls, exc: Exception) -> ExceptionDetails:
        return cls._format_exception(exc)


class BodyValidationError(Exception):
    """Raised for validation errors."""

    def __init__(self, exc: Exception):
        super().__init__(422, "Unprocessable entity")
        self.exc = exc


@frozen
class EventResponse:
    """An event."""

    id: str
    name: str
    description: Optional[str]
    date: date
    open: bool
    visible: bool


@frozen
class RegistrationListResponse:
    """A partial registration."""

    id: UUID
    state: RegistrationState
    event_id: str
    version: int
    date_created: datetime
    number: Optional[int]
    option_ids: list[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    preferred_name: Optional[str]


@frozen
class InterviewOption:
    """An available interview option."""

    id: str
    name: str


@frozen
class SelfServiceRegistrationResponse:
    """A sel- service registration."""

    registration: SelfServiceRegistration
    change_options: list[InterviewOption] = []


@frozen
class SelfServiceRegistrationListResponse:
    """A partial self-service registration."""

    registrations: list[SelfServiceRegistrationResponse]
    add_options: list[InterviewOption] = []


@frozen
class ModifierResponse:
    """A line item modifier."""

    name: str
    amount: int

    @classmethod
    def create(cls, modifier: Modifier) -> Self:
        return cls(modifier.name, modifier.amount)


@frozen
class LineItemResponse:
    """A line item."""

    name: str
    price: int
    total_price: int
    modifiers: Sequence[ModifierResponse] = ()
    description: Optional[str] = None

    @classmethod
    def create(cls, line_item: LineItem) -> Self:
        return cls(
            name=line_item.name,
            price=line_item.price,
            total_price=line_item.total_price,
            modifiers=tuple(ModifierResponse.create(m) for m in line_item.modifiers),
            description=line_item.description,
        )


@frozen
class PricingResultRegistrationResponse:
    """A registration in a pricing result."""

    registration_id: UUID
    line_items: Sequence[LineItemResponse] = ()
    name: Optional[str] = None

    @classmethod
    def create(cls, reg: PricingResultRegistration) -> Self:
        return cls(
            registration_id=reg.registration_id,
            line_items=tuple(LineItemResponse.create(li) for li in reg.line_items),
            name=reg.name,
        )


@frozen
class PricingResultResponse:
    """A cart pricing result."""

    receipt_url: Optional[str]
    date: Optional[str]
    registrations: Sequence[PricingResultRegistrationResponse]
    total_price: int
    modifiers: Sequence[ModifierResponse] = ()

    @classmethod
    def create(
        cls,
        pricing_result: PricingResult,
        receipt_url: Optional[str] = None,
        date: Optional[datetime] = None,
    ) -> Self:
        return cls(
            receipt_url=receipt_url,
            date=date.strftime("%c") if date is not None else None,
            registrations=tuple(
                PricingResultRegistrationResponse.create(reg)
                for reg in pricing_result.registrations
            ),
            total_price=pricing_result.total_price,
            modifiers=tuple(
                ModifierResponse.create(m) for m in pricing_result.modifiers
            ),
        )


@frozen
class CheckoutErrorResponse:
    """A checkout error including the invalid registration IDs."""

    errors: Mapping[str, str]


@frozen
class CreateCheckoutResponse:
    """A created checkout."""

    id: UUID
    service: str
    external_id: str
    data: dict[str, Any] = Factory(dict)


@frozen
class AccessCodeListResponse:
    """A list of partial access codes."""

    code: str
    event_id: str
    name: str
    used: bool


@frozen
class AccessCodeResponse:
    """An access code."""

    code: str
    event_id: str
    date_created: datetime
    date_expires: datetime
    name: Optional[str]
    used: bool
    data: AccessCodeSettings

    @classmethod
    def create(cls, entity: AccessCodeEntity) -> Self:
        return cls(
            code=entity.code,
            event_id=entity.event_id,
            date_created=entity.date_created,
            date_expires=entity.date_expires,
            name=entity.name,
            used=entity.used,
            data=entity.get_settings(),
        )