"""Main entry point."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar
import logging
import os
from blacksheep import Application, Content, Request, Response
from hypercorn import Config
from hypercorn.asyncio import serve
from rodi import ActivationScope, Container
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import uvloop
from cattrs.preconf.orjson import make_converter

from oes.registration.cattrs_binder import CattrsBinder, CattrsBodyError
from oes.registration.registration import RegistrationRepo
from oes.registration.routes.router import router
from oes.registration.serialization import configure_converter

services = Container()
app = Application(services=services, router=router)

_session_ctx: ContextVar[AsyncSession | None] = ContextVar("_session_ctx", default=None)


def run():
    """Main entry point."""
    uvloop.install()
    asyncio.run(_run())


@asynccontextmanager
async def _setup() -> AsyncGenerator[Application, None]:
    logging.basicConfig(level=logging.DEBUG)
    db_url = os.getenv("DB_URL", "")  # TODO: settings
    engine = create_async_engine(db_url)
    sessionmaker = async_sessionmaker(engine)
    services.add_instance(engine)
    services.add_instance(sessionmaker)

    services.add_scoped_by_factory(_session_factory)
    services.add_scoped(RegistrationRepo)

    _import_routes()

    app.middlewares.append(_transaction_middleware)

    converter = make_converter()
    configure_converter(converter)
    configure_converter(CattrsBinder.cattrs_converter)

    try:
        yield app
    finally:
        await engine.dispose()


def _session_factory(services: ActivationScope) -> AsyncSession:
    sessionmaker = services.get(async_sessionmaker)
    session = sessionmaker()
    _session_ctx.set(session)
    return session


async def _transaction_middleware(request, handler):
    try:
        response = await handler(request)
    except Exception as exc:
        session = _session_ctx.get()
        if session:
            await session.rollback()
        raise exc
    else:
        session = _session_ctx.get()
        if session and 200 <= response.status < 300:
            await session.commit()
        return response
    finally:
        session = _session_ctx.get()
        if session:
            await session.close()


@app.exception_handler(CattrsBodyError)
async def _body_error_handler(
    app: Application, request: Request, exc: CattrsBodyError
) -> Response:
    return Response(status=422, content=Content(b"text/plain", str(exc).encode()))


async def _run():
    config = Config()
    config.bind = ["0.0.0.0:8080"]

    async with _setup() as app:
        await serve(app, config)


def _import_routes():  # noqa
    from oes.registration.routes import registration
