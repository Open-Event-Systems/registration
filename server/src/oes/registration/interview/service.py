"""Interview service."""
import uuid
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, Optional

from cattrs import Converter
from httpx import AsyncClient
from oes.registration.interview.models import (
    InterviewListItem,
    InterviewResultRequest,
    InterviewResultResponse,
    StartInterviewRequest,
)
from oes.registration.models.config import Config
from oes.registration.serialization.json import JSONEncoder, default_encoder
from oes.template import Context


class InterviewService:
    """Interview service."""

    def __init__(
        self,
        config: Config,
        http_client: AsyncClient,
        converter: Converter,
        json_encoder: JSONEncoder = default_encoder,
    ):
        self._interview_url = config.interview.url
        self._api_key = config.interview.api_key
        self._http_client = http_client
        self._converter = converter
        self._json_encoder = json_encoder

    async def get_interviews(self) -> Sequence[InterviewListItem]:
        """Get a list of available interviews."""
        if not self._interview_url:
            return []

        req = await self._http_client.get(
            f"{self._interview_url}/interviews",
            headers={"Authorization": f"Bearer {self._api_key.get_secret_value()}"},
        )
        results = self._json_encoder.loads(req.content)
        return self._converter.structure(results, Sequence[InterviewListItem])

    async def start_interview(
        self,
        interview_id: str,
        *,
        target_url: str,
        submission_id: Optional[str] = None,
        context: Optional[Context] = None,
        initial_data: Optional[Context] = None,
        expiration_date: Optional[datetime] = None,
    ) -> Mapping[str, Any]:
        """Start an interview and return the state.

        Args:
            interview_id: The interview ID.
            target_url: The target URL.
            submission_id: A unique submission ID.
            context: The template context.
            initial_data: Initial data.
            expiration_date: A non-default expiration date.

        Returns:
            The initial state response.
        """
        req = StartInterviewRequest(
            target_url=target_url,
            submission_id=submission_id or uuid.uuid4().hex,
            expiration_date=expiration_date,
            context=context,
            data=initial_data,
        )
        body = self._converter.unstructure(req)
        body_bytes = self._json_encoder.dumps(body)

        result = await self._http_client.post(
            interview_id,
            content=body_bytes,
            headers={
                "Authorization": f"Bearer {self._api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
        )
        result.raise_for_status()
        return self._json_encoder.loads(result.content)

    async def get_result(
        self,
        state: str,
        *,
        target_url: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> Optional[InterviewResultResponse]:
        """Get the result of an interview.

        Args:
            state: The state string.
            target_url: The expected target URL.

        Returns:
            A :class:`InterviewResultResponse`, or ``None`` if the state is not
            complete, not valid, or expired.
        """
        if not self._interview_url:
            raise ValueError("Interview service URL not configured")

        req = InterviewResultRequest(state=state)
        body = self._converter.unstructure(req)
        body_bytes = self._json_encoder.dumps(body)

        result = await self._http_client.post(
            f"{self._interview_url}/result",
            content=body_bytes,
            headers={
                "Authorization": f"Bearer {self._api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
        )

        if result.status_code in (400, 409, 422):
            return None

        result.raise_for_status()

        result_data = self._json_encoder.loads(result.content)
        result_obj = self._converter.structure(result_data, InterviewResultResponse)

        if result_obj.get_valid(target_url=target_url, now=now):
            return result_obj
        else:
            return None
