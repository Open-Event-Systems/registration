"""Main entry points."""

import os

from cattr import Converter
from sanic import HTTPResponse, Request, Sanic
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from oes.registration.event import EventStatsRepo, EventStatsService
from oes.registration.registration import RegistrationService
from oes.utils.request import CattrsBody


def create_app() -> Sanic:
    """Main app entry point."""
    from oes.registration.registration import RegistrationRepo
    from oes.registration.routes import common, registration
    from oes.registration.serialization import configure_converter

    app = Sanic("Registration")

    configure_converter(common.response_converter.converter)

    app.blueprint(registration.routes, url_prefix="/events/<event_id>/registrations")

    app.ext.add_dependency(Converter, lambda: common.response_converter.converter)
    app.ext.add_dependency(CattrsBody)

    app.ext.add_dependency(AsyncSession, _get_session)

    app.ext.add_dependency(RegistrationRepo)
    app.ext.add_dependency(RegistrationService)

    app.ext.add_dependency(EventStatsRepo)
    app.ext.add_dependency(EventStatsService)

    app.before_server_start(_setup)
    app.after_server_stop(_shutdown)
    app.on_response(_txn_middleware)

    return app


async def _setup(app: Sanic):
    db_url = os.getenv("DB_URL", "")  # TODO: settings
    engine = create_async_engine(db_url)
    app.ctx.engine = engine
    app.ctx.session_factory = async_sessionmaker(engine)
    app.ext.dependency(app.ctx.session_factory)


async def _shutdown(app: Sanic):
    engine: AsyncEngine | None = getattr(app.ctx, "engine", None)
    if engine:
        await engine.dispose()


async def _txn_middleware(request: Request, response: HTTPResponse):
    session: AsyncSession | None = getattr(request.ctx, "session", None)
    if session:
        if 200 <= response.status < 300:
            await session.commit()
        else:
            await session.rollback()
        await session.close()


async def _get_session(
    request: Request, session_factory: async_sessionmaker
) -> AsyncSession:
    cur = getattr(request.ctx, "session", None)
    if cur:
        return cur
    session = session_factory()
    request.ctx.session = session
    return session
