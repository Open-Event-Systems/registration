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


def make_new_registration(
    event_id: str,
) -> Registration:
    """Make a new registration."""
    return _RegistrationImpl(
        {
            "id": generate_registration_id(),
            "event_id": event_id,
            "status": "created",
            "version": 1,
        }
    )


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
