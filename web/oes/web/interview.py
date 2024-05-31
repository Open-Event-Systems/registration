"""Interview service."""

import uuid
from collections.abc import Mapping
from typing import Any

import httpx
import orjson
from oes.web.config import Config, Event


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

    async def get_completed_interview(self, state: str) -> Mapping[str, Any] | None:
        """Get a completed interview."""
        res = await self.client.get(
            f"{self.config.interview_service_url}/completed-interviews/{state}"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return res.json()
