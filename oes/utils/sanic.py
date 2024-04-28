"""Sanic utils."""

from typing import AsyncContextManager

from cattrs import Converter
from cattrs.preconf.orjson import make_converter
from sanic import HTTPResponse, Request, Sanic
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from oes.utils.orm import get_session, set_session_factory
from oes.utils.request import CattrsBody

__all__ = [
    "setup_app",
    "setup_database",
]


def setup_app(app: Sanic, config: object = None, converter: Converter | None = None):
    """App setup boilerplate."""
    app.config.FALLBACK_ERROR_FORMAT = "json"

    app.ctx.config = config
    if config is not None:
        app.ext.dependency(config)

    converter = converter or make_converter()
    app.ext.add_dependency(CattrsBody)
    app.ext.add_dependency(Converter, lambda: converter)


def setup_database(app: Sanic, db_url: str):
    """Configure the app to manage a database engine."""
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    app.ctx.db_engine = engine
    app.ctx.db_session_factory = factory

    app.after_server_stop(_shutdown)

    app.on_response(_session_cleanup)
    app.ext.add_dependency(AsyncSession, _session_dependency)

    @app.on_request
    async def _set_factory_ctx(request: Request):
        # context is not copied, so set it here
        set_session_factory(factory)


async def _shutdown(app: Sanic):
    engine: AsyncEngine = app.ctx.db_engine
    await engine.dispose()


async def _session_dependency(request: Request) -> AsyncSession:
    cur_session: AsyncSession | None = getattr(request.ctx, "db_session", None)
    if cur_session is not None:
        return cur_session

    factory = request.app.ctx.db_session_factory

    session_ctx = get_session(factory=factory)
    session = await session_ctx.__aenter__()
    request.ctx.db_session_ctx = session_ctx
    request.ctx.db_session = session
    return session


async def _session_cleanup(request: Request, response: HTTPResponse):
    session_ctx: AsyncContextManager[AsyncSession] | None = getattr(
        request.ctx, "db_session_ctx", None
    )
    if session_ctx is not None:
        await session_ctx.__aexit__(None, None, None)
