"""Main entry points."""

import os
import sys

from cattr import Converter
from sanic import HTTPResponse, Request, Sanic
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from oes.registration_service.batch import BatchChangeService
from oes.registration_service.config import Config, get_config
from oes.registration_service.event import EventStatsRepo, EventStatsService
from oes.registration_service.registration import RegistrationService
from oes.utils.request import CattrsBody


def main():
    """CLI wrapper."""
    os.execlp(
        "sanic", sys.argv[0], "oes.registration_service.main:create_app", *sys.argv[1:]
    )


def create_app() -> Sanic:
    """Main app entry point."""
    from oes.registration_service.registration import RegistrationRepo
    from oes.registration_service.routes import batch, common, registration
    from oes.registration_service.serialization import configure_converter

    config = get_config()

    app = Sanic("Registration")
    app.config.FALLBACK_ERROR_FORMAT = "json"

    app.ctx.config = config

    configure_converter(common.response_converter.converter)

    app.blueprint(registration.routes, url_prefix="/events/<event_id>/registrations")
    app.blueprint(batch.routes, url_prefix="/events/<event_id>/batch-change")

    app.ext.add_dependency(Converter, lambda: common.response_converter.converter)
    app.ext.add_dependency(CattrsBody)

    app.ext.add_dependency(AsyncSession, _get_session)

    app.ext.add_dependency(RegistrationRepo)
    app.ext.add_dependency(RegistrationService)

    app.ext.add_dependency(EventStatsRepo)
    app.ext.add_dependency(EventStatsService)

    app.ext.add_dependency(BatchChangeService)

    app.before_server_start(_setup)
    app.after_server_stop(_shutdown)
    app.on_response(_txn_middleware)

    return app


async def _setup(app: Sanic):
    config: Config = app.ctx.config
    engine = create_async_engine(config.database.url)
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
