"""Registration module."""

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
from typing import Any, Literal

import httpx
import nanoid
import orjson
from attrs import frozen
from oes.web.config import Config
from oes.web.types import JSON
from typing_extensions import Self

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


class Registration(dict[str, Any]):
    """Registration dict."""

    def __new__(cls, arg: JSON | None = None) -> Self:
        inst = super().__new__(cls, arg or {})

        if not inst.get("id"):
            inst["id"] = generate_registration_id()

        if not inst.get("status"):
            inst["status"] = "created"

        if inst.get("version") is None:
            inst["version"] = 1

        return inst

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
            or not account_id
            and not email  # when auth is disabled
        )


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
        return [Registration(r) for r in res.json()]

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
        return Registration(res.json())

    async def check_batch_change(
        self,
        event_id: str,
        registrations: Iterable[Registration],
        access_codes: Mapping[str, str] | None = None,
    ) -> tuple[int, JSON]:
        """Check that cart changes can be applied.

        Returns:
            A pair of a response status code and a response body.
        """
        body = {
            "changes": [dict(r) for r in registrations],
            "access_codes": access_codes or {},
        }
        req_json = orjson.dumps(body)
        res = await self.client.post(
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/batch-change/check",
            content=req_json,
            headers={"Content-Type": "application/json"},
        )
        return res.status_code, res.json()

    async def apply_batch_change(
        self,
        event_id: str,
        registrations: Iterable[Registration],
        access_codes: Mapping[str, str] | None = None,
        payment_id: str | None = None,
        payment_body: JSON | None = None,
    ) -> tuple[int, JSON]:
        """Apply a batch change.

        Returns:
            A pair of a response status code and a response body.
        """
        if payment_id is not None:
            payment_url = (
                f"{self.config.payment_service_url}/payments/{payment_id}/update"
            )
        else:
            payment_url = None

        req_body = {
            "changes": [dict(r) for r in registrations],
            "payment_url": payment_url,
            "payment_body": payment_body,
            "access_codes": access_codes or {},
        }
        req_json = orjson.dumps(req_body)

        res = await self.client.post(
            f"{self.config.registration_service_url}/events"
            f"/{event_id}/batch-change/apply",
            content=req_json,
            headers={"Content-Type": "application/json"},
        )
        return res.status_code, res.json()


def make_new_registration(
    event_id: str,
) -> Registration:
    """Make a new registration."""
    return Registration(
        {
            "id": generate_registration_id(),
            "event_id": event_id,
            "status": "created",
            "version": 1,
        }
    )


_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_registration_id() -> str:
    """Generate a random registration ID."""
    return nanoid.generate(_alphabet, REGISTRATION_ID_LENGTH)
