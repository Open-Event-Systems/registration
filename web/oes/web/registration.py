"""Registration module."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

import httpx
import nanoid
import oes.web.interview
from attrs import evolve
from oes.utils.logic import evaluate
from oes.web.cart import CartService
from oes.web.config import Config, ConfigInterviewOption, Event

if TYPE_CHECKING:
    from oes.web.interview import (
        CompletedInterview,
        InterviewRegistration,
        InterviewRegistrationFields,
    )

REGISTRATION_ID_LENGTH = 14
"""Length of a registration ID."""


class AddRegistrationError(ValueError):
    """Raised when a registration cannot be added."""


class RegistrationService:
    """Registration service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

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
    ) -> Iterable[ConfigInterviewOption]:
        """Get available add options."""
        if access_code:
            opts = access_code.get("options", {})
            for opt in opts.get("add_options", []):
                yield ConfigInterviewOption(opt["id"], opt["title"])
            return

        ctx = {
            "event": event.get_template_context(),
        }
        for opt in event.self_service.add_options:
            if evaluate(opt.when, ctx):
                yield opt

    def get_change_options(
        self,
        event: Event,
        registration: Mapping[str, Any],
        access_code: Mapping[str, Any] | None,
    ) -> Iterable[ConfigInterviewOption]:
        """Get available change options."""
        if access_code:
            opts = access_code.get("options", {})
            for opt in opts.get("change_options", []):
                yield ConfigInterviewOption(opt["id"], opt["title"])
            return

        ctx = {
            "event": event.get_template_context(),
            "registration": registration,
        }
        for opt in event.self_service.change_options:
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
    config: Config,
) -> Mapping[str, Any]:
    """Add a completed interview to a cart."""
    event = config.get_event(completed_interview.event_id)
    if not event or not event.visible or not event.open:
        raise AddRegistrationError(f"Event not valid: {completed_interview.event_id}")

    all_registrations = list(completed_interview.registrations)

    if completed_interview.registration:
        all_registrations = [
            oes.web.interview.InterviewRegistration(
                registration=completed_interview.registration,
                meta=completed_interview.meta,
            ),
            *all_registrations,
        ]

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

    to_add = [
        await _make_cart_registration(
            completed_interview, r, event, access_code, registration_service
        )
        for r in all_registrations
    ]
    return await cart_service.add_to_cart(completed_interview.cart_id, to_add)


async def _make_cart_registration(
    interview: CompletedInterview,
    data: InterviewRegistration,
    event: Event,
    access_code_data: Mapping[str, Any] | None,
    service: RegistrationService,
) -> Mapping[str, Any]:
    exists, cur = await _get_current_registration(
        interview.event_id, data.registration.id, service
    )

    new_data = evolve(
        data.registration,
        id=data.registration.id or cur.get("id", ""),
        event_id=data.registration.event_id or event.id,
    )

    _check_can_add_registration(
        new_data,
        cur,
        interview.interview_id,
        not exists,
        event,
        access_code_data,
        service,
    )
    return {
        "id": cur.get("id", ""),
        "old": cur,
        "new": {
            "event_id": interview.event_id,
            **oes.web.interview.converter.unstructure(new_data),
        },
        "meta": (
            {
                "access_code": interview.access_code,
                **data.meta,
            }
            if interview.access_code
            else data.meta
        ),
    }


_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


async def _get_current_registration(
    event_id: str, id: str | None, service: RegistrationService
) -> tuple[bool, Mapping[str, Any]]:
    """Get the current registration data, or a default "empty" one."""
    orig_id = id
    id = id or generate_registration_id()
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
    registration: InterviewRegistrationFields,
    cur_registration: Mapping[str, Any],
    interview_id: str,
    is_new: bool,
    event: Event,
    access_code_data: Mapping[str, Any] | None,
    registration_service: RegistrationService,
):
    cur_version = cur_registration["version"]
    version = registration.version
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


def generate_registration_id() -> str:
    """Generate a random registration ID."""
    return nanoid.generate(_alphabet, REGISTRATION_ID_LENGTH)
