"""Storage module."""

import base64
import gzip
import hashlib
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import orjson
from cattrs import Converter
from immutabledict import immutabledict
from oes.interview.interview.interview import InterviewContext
from redis.asyncio import Redis
from typing_extensions import Self


class StorageService:
    """Storage service."""

    def __init__(self, url: str, converter: Converter):
        self._url = url
        self._client = Redis.from_url(url)
        self._converter = converter

    async def put(self, context: InterviewContext) -> str:
        """Store an :class:`InterviewContext`.

        Returns:
            A string key to reference the context.
        """
        state_only, context_only = self._unstructure(context)
        context_key = await self._store_context(
            context_only, context.state.date_expires
        )
        state_key = await self._store_state(
            state_only, context_key, context.state.date_expires
        )
        return state_key

    async def get(self, key: str) -> InterviewContext | None:
        """Get an :class:`InterviewContext`."""
        state_data = await self._client.get(b"oes.interview." + key.encode())
        if state_data is None:
            return None
        state = _from_bytes(state_data)
        context_key = state["context_key"]
        context_data = await self._client.get(b"oes.interview." + context_key.encode())
        if context_data is None:
            return None
        context = _from_bytes(context_data)
        full = {**context, "state": state["state"]}
        return self._converter.structure(full, InterviewContext)

    def _unstructure(
        self, context: InterviewContext
    ) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        data = self._converter.unstructure(context)
        context_only = dict(data)
        del context_only["state"]
        state_only = {"state": data["state"]}
        return state_only, context_only

    async def _store_context(
        self, context_only: Mapping[str, Any], exp: datetime
    ) -> str:
        key, bytes_ = _to_bytes(context_only)
        res = await self._client.set(
            b"oes.interview." + key.encode(), bytes_, exat=exp, nx=True
        )
        if res is None:
            await self._client.expireat(b"oes.interview." + key.encode(), exp, gt=True)
        return key

    async def _store_state(
        self, state_only: Mapping[str, Any], context_key: str, exp: datetime
    ) -> str:
        with_context_ref = {
            **state_only,
            "context_key": context_key,
        }
        key, bytes_ = _to_bytes(with_context_ref)
        await self._client.set(
            b"oes.interview." + key.encode(), bytes_, exat=exp, nx=True
        )
        return key

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_typ, exc_val, tb):
        await self.aclose()
        return False

    async def aclose(self):
        await self._client.aclose()


def _to_bytes(obj: Mapping[str, Any]) -> tuple[str, bytes]:
    bytes_ = orjson.dumps(obj, default=_default)
    h = hashlib.md5(bytes_, usedforsecurity=False)
    hash_ = base64.urlsafe_b64encode(h.digest()).decode().replace("=", "")

    compressed = gzip.compress(bytes_)

    return hash_, compressed


def _default(obj):
    if isinstance(obj, immutabledict):
        return dict(obj)
    else:
        raise TypeError(type(obj))


def _from_bytes(b: bytes) -> Mapping[str, Any]:
    decompressed = gzip.decompress(b)
    return orjson.loads(decompressed)
