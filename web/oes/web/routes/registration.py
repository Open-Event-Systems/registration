"""Registration module."""

from collections.abc import Iterable, Mapping
from typing import Any

from oes.utils.logic import evaluate
from oes.web.config import Config, Event, InterviewOption


class RegistrationService:
    """Registration service."""

    def __init__(self, config: Config):
        self.config = config
        self._events_by_id = {e.id: e for e in self.config.events}

    def get_event(self, event_id: str) -> Event | None:
        """Get an event by ID."""
        return self._events_by_id.get(event_id)

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
