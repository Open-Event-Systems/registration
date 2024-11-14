"""Interview module."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import httpx
from attrs import frozen
from cattrs.preconf.orjson import make_converter
from oes.checkin.config import Config
from oes.checkin.registration import Registration


@frozen
class CompletedInterview:
    """Completed interview body."""

    date_started: datetime
    date_expires: datetime
    target: str
    context: Mapping[str, Any]
    data: Mapping[str, Any]


class InterviewService:
    """Interview service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def start_interview(
        self,
        host: str,
        target: str,
        registration: Registration,
        session_id: str | None,
        interview_id: str,
    ) -> Mapping[str, Any]:
        """Start an interview."""
        url = f"{self.config.interview_service_url}/interviews/{interview_id}"
        context = {
            "session_id": session_id,
        }
        data = {
            "registration": dict(registration),
        }
        body = {
            "context": context,
            "data": data,
            "target": target,
        }
        res = await self.client.post(url, json=body, headers={"Host": host})
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
        return _converter.structure(res.json(), CompletedInterview)


_converter = make_converter()
