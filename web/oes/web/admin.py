"""Admin module."""

from collections.abc import Iterable

from oes.utils.logic import evaluate
from oes.web.config import AdminInterviewOption, Config
from oes.web.registration import Registration


class AdminService:
    """Admin service."""

    def __init__(self, config: Config):
        self.config = config

    def get_change_options(
        self, event_id: str, registration: Registration
    ) -> Iterable[AdminInterviewOption]:
        """Get available change options."""
        # TODO: pass in user role
        event = self.config.events[event_id]
        ctx = {
            "event": event.get_template_context(),
            "registration": dict(registration),
        }
        for opt in event.admin.change_options:
            if evaluate(opt.when, ctx):
                yield opt
