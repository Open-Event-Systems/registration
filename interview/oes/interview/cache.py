"""Cache module."""

import base64
import hashlib

import orjson
from cattrs import Converter
from oes.interview.interview.interview import InterviewContext
from redis.asyncio import Redis
from typing_extensions import Self


class CacheService:
    """Cache service."""

    def __init__(self, url: str, converter: Converter):
        self._url = url
        self._client = Redis.from_url(url)
        self._converter = converter

    async def put(self, context: InterviewContext) -> str:
        """Store an :class:`InterviewContext`.

        Returns:
            A string key to reference the context.
        """
        hash_, data = self._to_bytes(context)
        await self._client.set(
            b"oes.interview." + hash_.encode(),
            data,
            nx=True,
            exat=context.state.date_expires,
        )
        return hash_

    async def get(self, key: str) -> InterviewContext | None:
        """Get an :class:`InterviewContext`."""
        res = await self._client.get(b"oes.interview." + key.encode())
        if res is None:
            return None
        data = orjson.loads(res)
        loaded = self._converter.structure(data, InterviewContext)
        return loaded

    def _to_bytes(self, context: InterviewContext) -> tuple[str, bytes]:
        data = self._converter.unstructure(context)
        bytes_ = orjson.dumps(data)
        h = hashlib.md5(bytes_, usedforsecurity=False)
        hash_ = base64.urlsafe_b64encode(h.digest()).decode().replace("=", "")
        return hash_, bytes_

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_typ, exc_val, tb):
        await self.aclose()
        return False

    async def aclose(self):
        await self._client.aclose()
