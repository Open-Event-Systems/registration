"""Registration module."""

from collections.abc import Mapping
from typing import Any

import httpx
from oes.checkin.config import Config


class Registration(dict):
    """Registration object."""

    @property
    def id(self) -> str:
        """The ID."""
        return self["id"]

    @property
    def event_id(self) -> str:
        """The event ID."""
        return self["event_id"]


class RegistrationService:
    """Registration service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def get_registration(
        self, event_id: str, registration_id: str
    ) -> Registration | None:
        """Get a registration by ID."""
        url = f"{self.config.registration_service_url}/events/{event_id}/registrations/{registration_id}"
        res = await self.client.get(url)
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return Registration(res.json())

    async def apply_change(
        self, registration: Registration
    ) -> tuple[int, Mapping[str, Any]]:
        """Apply a change."""
        url = f"{self.config.registration_service_url}/events/{registration.event_id}/batch-change/apply"
        body = {"changes": [dict(registration)]}
        res = await self.client.post(url, json=body)
        if res.status_code == 204:
            return res.status_code, {}
        else:
            return res.status_code, res.json()
