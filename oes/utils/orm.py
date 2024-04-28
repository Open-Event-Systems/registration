"""ORM utils."""

from abc import ABC
from collections.abc import (
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    MutableMapping,
)
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from typing import (
    Annotated,
    Any,
    AsyncContextManager,
    ContextManager,
    Generic,
    ParamSpec,
    TypeAlias,
    TypeVar,
    overload,
)

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import mapped_column

__all__ = [
    "DEFAULT_MAX_STRING_LENGTH",
    "JSON",
    "TYPE_ANNOTATION_MAP",
    "NAMING_CONVENTION",
    "Repo",
    "set_session_factory",
    "get_session",
    "transaction",
]

DEFAULT_MAX_STRING_LENGTH = 300
"""Maximum string length."""

JSON: TypeAlias = Annotated[MutableMapping[str, Any], mapped_column(JSONB)]
"""JSON type."""

TYPE_ANNOTATION_MAP = {
    datetime: TIMESTAMP(timezone=True),
    str: String(DEFAULT_MAX_STRING_LENGTH),
}
"""Default type annotation map."""

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
"""Basic constraint naming convention."""

_K = TypeVar("_K")
_E = TypeVar("_E")


class Repo(ABC, Generic[_E, _K]):
    """Generic repo class."""

    entity_type: type[_E]

    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, entity: _E):
        """Add an entity to the database."""
        self.session.add(entity)

    async def get(self, id: _K, *, lock: bool = False) -> _E | None:
        """Get an entity by ID."""
        return await self.session.get(self.entity_type, id, with_for_update=lock)

    async def merge(self, entity: _E) -> _E:
        """Update an entity."""
        return await self.session.merge(entity)

    async def delete(self, entity: _E):
        """Delete an entity."""
        await self.session.delete(entity)


_session_factory_ctx: ContextVar[async_sessionmaker | None] = ContextVar(
    "_session_factory_ctx", default=None
)
_session_ctx: ContextVar[AsyncSession | None] = ContextVar("_session_ctx", default=None)


def set_session_factory(
    factory: async_sessionmaker,
) -> ContextManager[async_sessionmaker]:
    """Context manager to provide a :class:`async_sessionmaker` via context."""
    token = _session_factory_ctx.set(factory)

    @contextmanager
    def manager() -> Generator[async_sessionmaker, None, None]:
        try:
            yield factory
        finally:
            _session_factory_ctx.reset(token)

    return manager()


_P = ParamSpec("_P")
_R = TypeVar("_R")


class _TransactionFunc:
    """Context manager/decorator to a block of code in a transaction."""

    async def commit(self):
        """Commit the current session's transaction."""
        _cur_sess = _session_ctx.get()
        if _cur_sess is None:
            raise RuntimeError("No session in progress")
        await _cur_sess.commit()

    async def rollback(self):
        """Roll back the current session's transaction."""
        _cur_sess = _session_ctx.get()
        if _cur_sess is None:
            raise RuntimeError("No session in progress")
        await _cur_sess.rollback()

    @overload
    def __call__(
        self, func: Callable[_P, Awaitable[_R]]
    ) -> Callable[_P, Coroutine[None, None, _R]]: ...

    @overload
    def __call__(self) -> AsyncContextManager[AsyncSession]: ...

    def __call__(self, func: Callable | None = None) -> Any:
        """Decorate a function/run a block of code in a transaction."""
        if func is not None:
            return _transaction_decorator(func)
        else:
            return _transaction_ctx()


transaction = _TransactionFunc()


def _transaction_decorator(
    func: Callable[_P, Awaitable[_R]]
) -> Callable[_P, Coroutine[None, None, _R]]:
    @wraps(func)
    async def wrapper(*a: _P.args, **kw: _P.kwargs) -> _R:
        async with _transaction_ctx():
            return await func(*a, **kw)

    return wrapper


@asynccontextmanager
async def _transaction_ctx() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        try:
            yield session
        except BaseException as exc:
            await session.rollback()
            raise exc
        else:
            await session.commit()


@asynccontextmanager
async def get_session(
    reuse: bool = True, factory: async_sessionmaker | None = None
) -> AsyncGenerator[AsyncSession, None]:
    """Context manager that provides a :class:`AsyncSession`."""
    cur = _session_ctx.get()
    if cur and reuse:
        yield cur
    else:
        factory = factory if factory is not None else _session_factory_ctx.get()
        if factory is None:
            raise RuntimeError("No session factory set")
        async with _new_session(factory) as session:
            yield session


@asynccontextmanager
async def _new_session(
    factory: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = factory()
    token = _session_ctx.set(session)
    try:
        yield session
    finally:
        await session.close()
        _session_ctx.reset(token)
