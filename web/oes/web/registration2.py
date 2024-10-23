"""Registration module."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Literal

import httpx
import nanoid
from attrs import frozen
from cattrs.preconf.orjson import make_converter
from oes.web.config import Config
from oes.web.types import JSON, Registration

REGISTRATION_ID_LENGTH = 14
"""Length of a registration ID."""


@frozen
class InterviewOption:
    """An interview option."""

    id: str
    title: str
    direct: bool

    def get_target(
        self,
        base_url: str,
        event_id: str | None,
        cart_id: str | None,
        registration_id: str | None,
    ) -> str:
        """Get the target URL."""
        # TODO: urls
        if self.direct:
            return (
                f"{base_url}/events/{event_id}/registrations/{registration_id}/update"
            )
        else:
            return f"{base_url}/carts/{cart_id}/add"


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
    ) -> Sequence[Registration]:
        """Get registrations from the registration service."""
        url = (
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/registrations"
        )
        params = {}

        if account_id:
            params["account_id"] = account_id

        if email:
            params["email"] = email

        res = await self.client.get(url, params=params)
        res.raise_for_status()
        return _converter.structure(res.json(), Sequence[_RegistrationImpl])

    async def get_registration(
        self, event_id: str, registration_id: str
    ) -> Registration | None:
        """Get a registration from the registration service."""
        url = (
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/registrations/{registration_id}"
        )
        res = await self.client.get(url)
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return _converter.structure(res.json(), _RegistrationImpl)

    # def get_add_options(
    #     self, event: Event, access_code: Mapping[str, Any] | None
    # ) -> Iterable[InterviewOption]:
    #     """Get available add options."""
    #     if access_code:
    #         opts = access_code.get("options", {})
    #         for opt in opts.get("add_options", []):
    #             yield InterviewOption(opt["id"], opt["title"])
    #         return

    #     ctx = {
    #         "event": event.get_template_context(),
    #     }
    #     for opt in event.self_service.add_options:
    #         if evaluate(opt.when, ctx):
    #             yield opt

    # def get_change_options(
    #     self,
    #     event: Event,
    #     registration: Mapping[str, Any],
    #     access_code: Mapping[str, Any] | None,
    # ) -> Iterable[InterviewOption]:
    #     """Get available change options."""
    #     if access_code:
    #         opts = access_code.get("options", {})
    #         for opt in opts.get("change_options", []):
    #             yield InterviewOption(opt["id"], opt["title"])
    #         return

    #     ctx = {
    #         "event": event.get_template_context(),
    #         "registration": registration,
    #     }
    #     for opt in event.self_service.change_options:
    #         if evaluate(opt.when, ctx):
    #             yield opt

    # def is_interview_allowed(
    #     self,
    #     interview_id: str,
    #     event: Event,
    #     registration: Mapping[str, Any] | None,
    #     access_code: Mapping[str, Any] | None,
    # ) -> bool:
    #     """Check if an interview is allowed."""
    #     if access_code is not None:
    #         return self._is_interview_allowed_access_code(
    #             interview_id, registration, access_code
    #         )
    #     if registration is None:
    #         return any(o.id == interview_id for o in self.get_add_options(event, None))
    #     else:
    #         return any(
    #             o.id == interview_id
    #             for o in self.get_change_options(event, registration, None)
    #         )

    # def _is_interview_allowed_access_code(
    #     self,
    #     interview_id: str,
    #     registration: Mapping[str, Any] | None,
    #     access_code_data: Mapping[str, Any],
    # ) -> bool:
    #     opts = access_code_data.get("options", {})
    #     if registration is None:
    #         add_options = opts.get("add_options", [])
    #         return any(opt["id"] == interview_id for opt in add_options)
    #     else:
    #         reg_ids = opts.get("registration_ids", [])
    #         if reg_ids and registration.get("id") not in reg_ids:
    #             return False
    #         change_options = opts.get("change_options", [])
    #         return any(opt["id"] == interview_id for opt in change_options)

    # async def check_batch_change(
    #     self, event_id: str, cart_data: Mapping[str, Any]
    # ) -> tuple[int, Mapping[str, Any]]:
    #     """Check that cart changes can be applied.

    #     Returns:
    #         A pair of a response status code and a response body.
    #     """
    #     changes = [r.get("new", {}) for r in cart_data.get("registrations", [])]
    #     body = {
    #         "changes": changes,
    #         "access_codes": _get_access_codes(cart_data),
    #     }
    #     res = await self.client.post(
    #         f"{self.config.registration_service_url}/events"
    #         f"/{event_id}/batch-change/check",
    #         json=body,
    #     )
    #     return res.status_code, res.json()

    # async def apply_batch_change(
    #     self,
    #     event_id: str,
    #     cart_data: Mapping[str, Any],
    #     payment_id: str | None = None,
    #     payment_body: Mapping[str, Any] | None = None,
    # ) -> tuple[int, Mapping[str, Any]]:
    #     """Apply a batch change.

    #     Returns:
    #         A pair of a response status code and a response body.
    #     """
    #     changes = [r.get("new", {}) for r in cart_data.get("registrations", [])]

    #     if payment_id is not None:
    #         payment_url = (
    #             f"{self.config.payment_service_url}/payments/{payment_id}/update"
    #         )
    #     else:
    #         payment_url = None

    #     req_body = {
    #         "changes": changes,
    #         "payment_url": payment_url,
    #         "payment_body": payment_body,
    #         "access_codes": _get_access_codes(cart_data),
    #     }

    #     res = await self.client.post(
    #         f"{self.config.registration_service_url}/events"
    #         f"/{event_id}/batch-change/apply",
    #         json=req_body,
    #     )
    #     return res.status_code, res.json()

    # async def get_access_code(
    #     self, event_id: str, code: str
    # ) -> Mapping[str, Any] | None:
    #     """Get an access code by ID."""
    #     res = await self.client.get(
    #         f"{self.config.registration_service_url}/events/{event_id}"
    #         f"/access-codes/{code}"
    #     )
    #     if res.status_code == 404:
    #         return None
    #     res.raise_for_status()
    #     return res.json()


class _RegistrationImpl(dict[str, Any]):

    @property
    def id(self) -> str:
        return self["id"]

    @property
    def event_id(self) -> str:
        return self["event_id"]

    @property
    def status(self) -> Literal["pending", "created", "canceled"]:
        return self["status"]

    @property
    def version(self) -> int:
        return self["version"]

    @property
    def date_created(self) -> datetime:
        return self["date_created"]

    @property
    def date_updated(self) -> datetime | None:
        return self["date_updated"]

    def has_permission(self, account_id: str | None, email: str | None) -> bool:
        return (
            bool(account_id)
            and account_id == self.get("account_id")
            or bool(email)
            and email == self.get("email")
        )


def make_registration(
    data: JSON,
) -> Registration:
    """Make a registration."""
    return _RegistrationImpl(data)


def make_placeholder_registration(reg: Registration) -> Registration:
    """Create a placeholder registration."""
    return _RegistrationImpl(
        {
            "id": reg.id,
            "event_id": reg.event_id,
            "status": "pending",
            "version": 1,
        }
    )


_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_registration_id() -> str:
    """Generate a random registration ID."""
    return nanoid.generate(_alphabet, REGISTRATION_ID_LENGTH)


_converter = make_converter()
