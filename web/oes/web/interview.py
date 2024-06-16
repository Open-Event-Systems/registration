"""Interview service."""

import uuid
from collections.abc import Mapping, Sequence
from typing import Any

import httpx
import orjson
from attrs import frozen
from oes.web.config import Config, Event
from typing_extensions import Self


@frozen
class CompletedInterview:
    """Completed interview body."""

    data: Mapping[str, Any]
    """Result data."""

    context: Mapping[str, Any]
    """Interview context."""

    target: str
    """The target URL."""

    meta: Mapping[str, Any]
    """Interview metadata."""

    cart_id: str
    """The cart ID to modify."""

    interview_id: str
    """The interview used."""

    event_id: str
    """The event id."""

    access_code: str | None
    """The access code used."""

    registration: Mapping[str, Any] | None
    """The registration."""

    registrations: Sequence[Mapping[str, Any]]
    """The list of registrations."""

    @classmethod
    def parse(cls, body: Mapping[str, Any]) -> Self:
        """Parse a completed interview body."""
        data = body["data"]
        context = body["context"]
        target = body["target"]
        meta = data.get("meta", {})
        cart_id = context["cart_id"]
        interview_id = context["interview_id"]
        event_id = context["event_id"]
        access_code = context.get("access_code")
        registration = data.get("registration")
        registrations = data.get("registrations", [])
        return cls(
            data,
            context,
            target,
            meta,
            cart_id,
            interview_id,
            event_id,
            access_code,
            registration,
            registrations,
        )


class InterviewService:
    """Interview service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def start_interview(
        self,
        event: Event,
        interview_id: str,
        cart_id: str,
        target: str,
        account_id: str | None,
        registration: Mapping[str, Any] | None,
        access_code: str | None,
    ) -> Mapping[str, Any]:
        """Start an interview."""
        if registration is None:
            registration = {
                "id": str(uuid.uuid4()),
                "status": "created",
                "event_id": event.id,
                "version": 1,
                "account_id": account_id,
            }

        url = f"{self.config.interview_service_url}/interviews/{interview_id}"
        body = {
            "context": {
                "event": event.get_template_context(),
                "event_id": event.id,
                "interview_id": interview_id,
                "cart_id": cart_id,
                "access_code": access_code,
            },
            "data": {
                "registration": registration,
                "meta": {},
            },
            "target": target,
        }

        body_bytes = orjson.dumps(body)
        res = await self.client.post(
            url, content=body_bytes, headers={"Content-Type": "application/json"}
        )
        res.raise_for_status()
        return res.json()

    async def get_completed_interview(self, state: str) -> CompletedInterview | None:
        """Get a completed interview."""
        res = await self.client.get(
            f"{self.config.interview_service_url}/completed-interviews/{state}"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return CompletedInterview.parse(res.json())
