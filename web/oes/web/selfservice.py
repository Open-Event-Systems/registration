"""Self service module."""

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from attrs import frozen
from oes.utils.logic import evaluate
from oes.utils.mapping import merge_mapping
from oes.utils.template import TemplateContext
from oes.web.access_code import AccessCode, AccessCodeInterviewOption, AccessCodeService
from oes.web.config import Config, Event, RegistrationDisplay
from oes.web.registration2 import (
    InterviewOption,
    RegistrationService,
    make_new_registration,
)
from oes.web.types import Registration
from typing_extensions import Self


@frozen
class SelfServiceRegistration:
    """Self service registration."""

    id: str
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    header_color: str | None = None
    header_image: str | None = None
    change_options: Sequence[InterviewOption] = ()

    @classmethod
    def from_registration(
        cls,
        display: RegistrationDisplay,
        event_ctx: TemplateContext,
        change_opts: Sequence[InterviewOption],
        registration: Registration,
    ) -> Self:
        """Create from a registration object."""
        ctx = {
            "event": event_ctx,
            "registration": dict(registration),
        }
        title = display.title.render(ctx)
        subtitle = display.subtitle.render(ctx) if display.subtitle else None
        description = display.description.render(ctx) if display.description else None
        header_color = (
            display.header_color.render(ctx) if display.header_color else None
        )
        header_image = (
            display.header_image.render(ctx) if display.header_image else None
        )
        return cls(
            registration["id"],
            title,
            subtitle,
            description,
            header_color,
            header_image,
            tuple(change_opts),
        )


class SelfServiceService:
    """Self service service."""

    def __init__(
        self,
        config: Config,
        registration_service: RegistrationService,
        access_code_service: AccessCodeService,
    ):
        self.config = config
        self.registration_service = registration_service
        self.access_code_service = access_code_service

    async def get_registrations_and_options(
        self,
        event_id: str,
        account_id: str | None,
        email: str | None,
        access_code: AccessCode | None,
    ) -> Sequence[tuple[Registration, Iterable[InterviewOption]]]:
        """Get a user's registrations and change options."""
        registrations = await self.get_registrations(
            event_id, account_id, email, access_code
        )
        res = []
        for registration in registrations:
            options = self.get_change_options(event_id, registration, access_code)
            res.append((registration, options))
        return res

    async def get_registrations(
        self,
        event_id: str,
        account_id: str | None,
        email: str | None,
        access_code: AccessCode | None,
    ) -> Sequence[Registration]:
        """Get a user's registrations."""
        if access_code and len(access_code.options.registration_ids) > 0:
            return await self._get_access_code_registrations(event_id, access_code)
        else:
            return await self.registration_service.get_registrations(
                event_id=event_id, account_id=account_id, email=email
            )

    async def _get_access_code_registrations(
        self, event_id: str, access_code: AccessCode
    ) -> list[Registration]:
        registrations = []
        for id in access_code.options.registration_ids:
            reg = await self.registration_service.get_registration(event_id, id)
            if reg is not None:
                registrations.append(reg)
        return registrations

    def get_add_options(
        self, event_id: str, access_code: AccessCode | None
    ) -> Iterable[InterviewOption]:
        """Get available add interview options."""
        if access_code:
            for opt in access_code.options.add_options:
                yield InterviewOption(opt.id, opt.title, opt.direct)
        else:
            event = self.config.events[event_id]
            event_ctx = event.get_template_context()
            for opt in event.self_service.add_options:
                ctx = {"event": event_ctx}
                if evaluate(opt.when, ctx):
                    yield InterviewOption(opt.id, opt.title, opt.direct)

    def get_change_options(  # noqa: CCR001
        self, event_id: str, registration: Registration, access_code: AccessCode | None
    ) -> Iterable[InterviewOption]:
        """Get available change interview options."""
        if access_code:
            if (
                len(access_code.options.registration_ids) > 0
                and registration.id not in access_code.options.registration_ids
            ):
                return
            for opt in access_code.options.change_options:
                yield InterviewOption(opt.id, opt.title, opt.direct)
        else:
            event = self.config.events[event_id]
            event_ctx = event.get_template_context()
            for opt in event.self_service.change_options:
                ctx = {"event": event_ctx, "registration": dict(registration)}
                if evaluate(opt.when, ctx):
                    yield InterviewOption(opt.id, opt.title, opt.direct)


def get_interview_data(
    event: Event,
    registration: Registration | None,
    interview_id: str,
    access_code: AccessCode | None,
    email: str | None,
    account_id: str | None,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Get the context and data for an interview."""
    opt = (
        get_access_code_interview(interview_id, registration, access_code)
        if access_code
        else None
    )

    if opt:
        context = opt.context
        opt_data = opt.initial_data
    else:
        context = {}
        opt_data = {}

    data = {}

    reg_data = dict(
        registration if registration is not None else make_new_registration(event.id)
    )

    context = merge_mapping(
        context,
        {
            "event_id": event.id,
            "event": event.get_template_context(),
            "account_id": account_id,
            "email": email,
            "access_code": access_code.code if access_code else None,
        },
    )

    data = merge_mapping(
        data,
        {
            "meta": {**({"access_code": access_code.code} if access_code else {})},
            "registration": {
                **reg_data,
                **({"account_id": account_id} if account_id else {}),
            },
        },
    )

    data = merge_mapping(data, opt_data)

    return context, data


def options_include(
    interview_id: str,
    options: Iterable[InterviewOption],
) -> bool:
    """Get whether interview options include the given ID."""
    return any(o.id == interview_id for o in options)


def get_access_code_interview(
    interview_id: str,
    registration: Registration | None,
    access_code: AccessCode,
) -> AccessCodeInterviewOption | None:
    """Get the interview option for an access code."""
    opts = (
        access_code.options.change_options
        if registration is not None
        else access_code.options.add_options
    )

    for opt in opts:
        if opt.id == interview_id:
            return opt
    return None
