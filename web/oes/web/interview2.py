"""Interview service."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

import httpx
import orjson
from attrs import field, frozen
from cattrs.preconf.orjson import make_converter
from oes.utils.mapping import merge_mapping
from oes.web.config import Config
from oes.web.registration2 import Registration, generate_registration_id
from oes.web.types import JSON


@frozen
class InterviewRegistration:
    """Interview registration object."""

    registration: Registration
    meta: JSON = field(factory=dict)


@frozen
class CompletedInterview:
    """Completed interview body."""

    date_started: datetime
    date_expires: datetime
    target: str
    context: JSON
    data: JSON


@frozen
class InterviewState:
    """Interview state object."""

    state: str
    completed: bool
    target: str
    content: JSON | None = None


class InterviewService:
    """Interview service."""

    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def start_interview(
        self,
        host: str,
        interview_id: str,
        target: str,
        context: Mapping[str, Any] | None,
        initial_data: Mapping[str, Any] | None,
    ) -> InterviewState:
        """Start an interview."""
        url = f"{self.config.interview_service_url}/interviews/{interview_id}"
        body = {
            "context": context,
            "data": initial_data,
            "target": target,
        }

        body_bytes = orjson.dumps(body)
        res = await self.client.post(
            url,
            content=body_bytes,
            headers={"Content-Type": "application/json", "Host": host},
        )
        res.raise_for_status()
        return _converter.structure(res.json(), InterviewState)

    async def get_completed_interview(self, state: str) -> CompletedInterview | None:
        """Get a completed interview."""
        res = await self.client.get(
            f"{self.config.interview_service_url}/completed-interviews/{state}"
        )
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return _converter.structure(res.json(), CompletedInterview)


def get_interview_registrations(
    interview: CompletedInterview,
) -> Sequence[InterviewRegistration]:
    """Get registration objects from an interview."""
    event_id = interview.context["event_id"]
    registrations = []

    reg = interview.data.get("registration")
    if reg:
        registrations.append(
            InterviewRegistration(
                _with_required_fields(event_id, reg),
                interview.data.get("meta", {}),
            )
        )

    for int_reg in interview.data.get("registrations", []):
        registrations.append(
            InterviewRegistration(
                _with_required_fields(event_id, int_reg.get("registration") or {}),
                int_reg.get("meta", {}),
            )
        )

    return registrations


def _with_required_fields(event_id: str, reg: JSON) -> Registration:
    data = dict(reg)
    id = data.get("id") or generate_registration_id()
    merged = merge_mapping(
        {
            "status": "created",
            "version": 1,
            "event_id": event_id,
            "date_created": datetime.now().astimezone(),
        },
        data,
    )
    return Registration({**merged, "id": id})


_converter = make_converter()
