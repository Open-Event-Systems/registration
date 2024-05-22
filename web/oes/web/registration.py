"""Registration module."""

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import httpx
from oes.utils.logic import evaluate
from oes.web.config import Config, Event, InterviewOption


class RegistrationService:
    """Registration service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client
        self._events_by_id = {e.id: e for e in self.config.events}

    def get_event(self, event_id: str) -> Event | None:
        """Get an event by ID."""
        return self._events_by_id.get(event_id)

    async def get_registrations(self, event_id: str) -> Sequence[Mapping[str, Any]]:
        """Get registrations from the registration service."""
        # TODO: filter by account/email
        url = f"{self.config.registration_service_url}/events/{event_id}/registrations"
        res = await self.client.get(url)
        return res.json()

    def get_add_options(self, event: Event) -> Iterable[InterviewOption]:
        """Get available add options."""
        ctx = {
            "event": event.get_template_context(),
        }
        for opt in event.add_options:
            if evaluate(opt.when, ctx):
                yield opt

    def get_change_options(
        self, event: Event, registration: Mapping[str, Any]
    ) -> Iterable[InterviewOption]:
        """Get available change options."""
        ctx = {
            "event": event.get_template_context(),
            "registration": registration,
        }
        for opt in event.change_options:
            if evaluate(opt.when, ctx):
                yield opt

    def is_interview_allowed(
        self, interview_id: str, event: Event, registration: Mapping[str, Any] | None
    ) -> bool:
        """Check if an interview is allowed."""
        if registration is None:
            return any(o.id == interview_id for o in self.get_add_options(event))
        else:
            return any(
                o.id == interview_id
                for o in self.get_change_options(event, registration)
            )
