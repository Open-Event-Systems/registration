"""Access code module."""

from collections.abc import Sequence
from datetime import datetime

import httpx
from attrs import field, frozen
from cattrs.preconf.orjson import make_converter
from oes.web.config import Config
from oes.web.types import JSON


@frozen
class AccessCodeInterviewOption:
    """Access code interview option."""

    id: str
    title: str
    direct: bool = False
    context: JSON = field(factory=dict)
    initial_data: JSON = field(factory=dict)


@frozen
class AccessCodeOptions:
    """Access code options."""

    add_options: Sequence[AccessCodeInterviewOption]
    change_options: Sequence[AccessCodeInterviewOption]
    registration_ids: Sequence[str]


@frozen
class AccessCode:
    """Access code type."""

    code: str
    date_created: datetime
    date_expires: datetime
    used: bool
    name: str
    options: AccessCodeOptions
    valid: bool


class AccessCodeService:
    def __init__(self, config: Config, client: httpx.AsyncClient):
        self.config = config
        self.client = client

    async def get_access_code(self, event_id: str, code: str) -> AccessCode | None:
        """Get an access code."""
        url = (
            f"{self.config.registration_service_url}/events/{event_id}"
            f"/access-codes/{code}"
        )
        res = await self.client.get(url)
        if res.status_code == 404:
            return None
        res.raise_for_status()
        return _converter.structure(res.json(), AccessCode)


_converter = make_converter()
