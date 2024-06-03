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

    async def get_registrations(
        self,
        *,
        event_id: str,
        account_id: str | None = None,
        email: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        """Get registrations from the registration service."""
        url = f"{self.config.registration_service_url}/events/{event_id}/registrations"
        params = {}

        if account_id:
            params["account_id"] = account_id

        if email:
            params["email"] = email

        res = await self.client.get(url, params=params)
        res.raise_for_status()
        return res.json()

    async def get_registration(
        self, event_id: str, registration_id: str
    ) -> Mapping[str, Any] | None:
        """Get a registration from the registration service."""
        url = (
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/registrations/{registration_id}"
        )
        res = await self.client.get(url)
        if res.status_code == 404:
            return None
        res.raise_for_status()
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
        self,
        interview_id: str,
        event: Event,
        registration: Mapping[str, Any] | None,
        access_code_data: Mapping[str, Any] | None,
    ) -> bool:
        """Check if an interview is allowed."""
        if access_code_data is not None:
            return self._is_interview_allowed_access_code(
                interview_id, registration, access_code_data
            )
        if registration is None:
            return any(o.id == interview_id for o in self.get_add_options(event))
        else:
            return any(
                o.id == interview_id
                for o in self.get_change_options(event, registration)
            )

    def _is_interview_allowed_access_code(
        self,
        interview_id: str,
        registration: Mapping[str, Any] | None,
        access_code_data: Mapping[str, Any],
    ) -> bool:
        opts = access_code_data.get("options", {})
        if registration is None:
            add_options = opts.get("add_options", [])
            return any(opt["id"] == interview_id for opt in add_options)
        else:
            reg_ids = opts.get("registration_ids", [])
            if reg_ids and registration.get("id") not in reg_ids:
                return False
            change_options = opts.get("change_options", [])
            return any(opt["id"] == interview_id for opt in change_options)

    async def check_batch_change(
        self, event_id: str, cart_data: Mapping[str, Any]
    ) -> tuple[int, Mapping[str, Any]]:
        """Check that cart changes can be applied.

        Returns:
            A pair of a response status code and a response body.
        """
        changes = [r.get("new", {}) for r in cart_data.get("registrations", [])]
        body = {
            "changes": changes,
            "access_codes": _get_access_codes(cart_data),
        }
        res = await self.client.post(
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/batch-change/check",
            json=body,
        )
        return res.status_code, res.json()

    async def apply_batch_change(
        self,
        event_id: str,
        cart_data: Mapping[str, Any],
        payment_id: str | None = None,
        payment_body: Mapping[str, Any] | None = None,
    ) -> tuple[int, Mapping[str, Any]]:
        """Apply a batch change.

        Returns:
            A pair of a response status code and a response body.
        """
        changes = [r.get("new", {}) for r in cart_data.get("registrations", [])]

        if payment_id is not None:
            payment_url = (
                f"{self.config.payment_service_url}/payments/{payment_id}/update"
            )
        else:
            payment_url = None

        req_body = {
            "changes": changes,
            "payment_url": payment_url,
            "payment_body": payment_body,
            "access_codes": _get_access_codes(cart_data),
        }

        res = await self.client.post(
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/batch-change/apply",
            json=req_body,
        )
        return res.status_code, res.json()

    async def get_access_code(
        self, event_id: str, code: str
    ) -> Mapping[str, Any] | None:
        """Get an access code by ID."""
        res = await self.client.get(
            f"{self.config.registration_service_url}/events/{event_id}"
            f"/access-codes/{code}"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()


def _get_access_codes(cart_data: Mapping[str, Any]) -> Mapping[str, Any]:
    codes = {}
    for registration in cart_data.get("registrations", []):
        meta = registration.get("meta", {})
        access_code = meta.get("access_code")
        if access_code:
            codes[registration["id"]] = access_code
    return codes
