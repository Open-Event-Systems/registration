"""Self service module."""

from collections.abc import Iterable, Sequence

from attrs import frozen
from oes.utils.logic import evaluate
from oes.utils.template import TemplateContext
from oes.web.access_code import AccessCode, AccessCodeService
from oes.web.config import Config, RegistrationDisplay
from oes.web.registration2 import InterviewOption, RegistrationService
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

    async def get_registrations(
        self,
        event_id: str,
        account_id: str,
        email: str | None,
        access_code: AccessCode | None,
    ) -> Sequence[Registration]:
        """Get a user's registrations."""
        if access_code:
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
