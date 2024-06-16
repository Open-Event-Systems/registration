"""Registration module."""

import uuid
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import httpx
from oes.utils.logic import evaluate
from oes.web.cart import CartService
from oes.web.config import Config, Event, InterviewOption
from oes.web.interview import CompletedInterview


class AddRegistrationError(ValueError):
    """Raised when a registration cannot be added."""


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

    def get_add_options(
        self, event: Event, access_code: Mapping[str, Any] | None
    ) -> Iterable[InterviewOption]:
        """Get available add options."""
        if access_code:
            opts = access_code.get("options", {})
            for opt in opts.get("add_options", []):
                yield InterviewOption(opt["id"], opt["title"])
            return

        ctx = {
            "event": event.get_template_context(),
        }
        for opt in event.add_options:
            if evaluate(opt.when, ctx):
                yield opt

    def get_change_options(
        self,
        event: Event,
        registration: Mapping[str, Any],
        access_code: Mapping[str, Any] | None,
    ) -> Iterable[InterviewOption]:
        """Get available change options."""
        if access_code:
            opts = access_code.get("options", {})
            for opt in opts.get("change_options", []):
                yield InterviewOption(opt["id"], opt["title"])
            return

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
        access_code: Mapping[str, Any] | None,
    ) -> bool:
        """Check if an interview is allowed."""
        if access_code is not None:
            return self._is_interview_allowed_access_code(
                interview_id, registration, access_code
            )
        if registration is None:
            return any(o.id == interview_id for o in self.get_add_options(event, None))
        else:
            return any(
                o.id == interview_id
                for o in self.get_change_options(event, registration, None)
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


async def add_to_cart(  # noqa: CCR001
    completed_interview: CompletedInterview,
    registration_service: RegistrationService,
    cart_service: CartService,
) -> Mapping[str, Any]:
    """Add a completed interview to a cart."""
    event = registration_service.get_event(completed_interview.event_id)
    if not event or not event.visible or not event.open:
        raise AddRegistrationError(f"Event not valid: {completed_interview.event_id}")

    all_registrations = (
        [completed_interview.registration, *completed_interview.registrations]
        if completed_interview.registration
        else [*completed_interview.registrations]
    )
    cur_registrations = [
        (
            r,
            await _get_current_registration(
                completed_interview.event_id, r.get("id"), registration_service
            ),
        )
        for r in all_registrations
    ]
    by_id = {c.get("id", ""): (e, r, c) for r, (e, c) in cur_registrations}

    access_code = (
        await registration_service.get_access_code(
            completed_interview.event_id, completed_interview.access_code
        )
        if completed_interview.access_code
        else None
    )
    if completed_interview.access_code and (
        not access_code or not access_code.get("valid")
    ):
        raise AddRegistrationError(
            f"Invalid access code: {completed_interview.access_code}"
        )

    cart = await cart_service.get_cart(completed_interview.cart_id)
    if not cart:
        raise AddRegistrationError(f"Cart not found: {completed_interview.cart_id}")

    to_add = []
    for reg_id, (exist, reg_data, cur) in by_id.items():
        _check_can_add_registration(
            reg_data,
            cur,
            completed_interview.interview_id,
            not exist,
            event,
            access_code,
            registration_service,
        )
        to_add.append(
            {
                "id": reg_id,
                "old": cur,
                "new": reg_data,
                "meta": (
                    {
                        "access_code": completed_interview.access_code,
                        **completed_interview.meta,
                    }
                    if completed_interview.access_code
                    else completed_interview.meta
                ),
            },
        )
    return await cart_service.add_to_cart(completed_interview.cart_id, to_add)


async def _get_current_registration(
    event_id: str, id: str | None, service: RegistrationService
) -> tuple[bool, Mapping[str, Any]]:
    """Get the current registration data, or a default "empty" one."""
    # TODO: generate properly once no longer using uuids
    orig_id = id
    id = id or str(uuid.uuid4())
    cur = await service.get_registration(event_id, orig_id) if orig_id else None
    if cur:
        return True, cur
    else:
        return False, {
            "id": id,
            "event_id": event_id,
            "status": "pending",
            "version": 1,
        }


def _check_can_add_registration(
    registration: Mapping[str, Any],
    cur_registration: Mapping[str, Any],
    interview_id: str,
    is_new: bool,
    event: Event,
    access_code_data: Mapping[str, Any] | None,
    registration_service: RegistrationService,
):
    cur_version = cur_registration["version"]
    version = registration.get("version", 1)
    if version != cur_version:
        raise AddRegistrationError(f"Version mismatch: {version} != {cur_version}")

    if not registration_service.is_interview_allowed(
        interview_id, event, cur_registration if not is_new else None, access_code_data
    ):
        raise AddRegistrationError(f"Interview not allowed: {interview_id}")


def _get_access_codes(cart_data: Mapping[str, Any]) -> Mapping[str, Any]:
    codes = {}
    for registration in cart_data.get("registrations", []):
        meta = registration.get("meta", {})
        access_code = meta.get("access_code")
        if access_code:
            codes[registration["id"]] = access_code
    return codes
