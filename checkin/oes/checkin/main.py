"""Main entry points."""

import os
import sys

import httpx
from oes.checkin.checkin import CheckInRepo, CheckInService
from oes.checkin.config import get_config
from oes.checkin.interview import InterviewService
from oes.checkin.registration import RegistrationService
from oes.utils.sanic import setup_app, setup_database
from sanic import Sanic
from sanic.worker.manager import WorkerManager
from sanic_ext import Extend

WorkerManager.THRESHOLD = 1200  # type: ignore


def main():
    """CLI wrapper."""
    os.execlp(
        "sanic",
        sys.argv[0],
        "--single-process",
        "oes.checkin.main:create_app",
        *sys.argv[1:],
    )


def create_app() -> Sanic:
    """Main app entry point."""
    from oes.checkin.routes import routes

    config = get_config()

    app = Sanic("CheckIn", configure_logging=False)
    app.config.PROXIES_COUNT = 1
    # app.config.CORS_ORIGINS = config.allowed_origins
    Extend(app)
    setup_app(app, config)
    setup_database(app, config.db_url)

    app.blueprint(routes)
    app.ext.add_dependency(CheckInRepo)
    app.ext.add_dependency(CheckInService)
    app.ext.add_dependency(RegistrationService)
    app.ext.add_dependency(InterviewService)

    @app.before_server_start
    async def setup_httpx(app: Sanic):
        client = httpx.AsyncClient()
        app.ctx.httpx = client
        app.ext.dependency(client)

    @app.after_server_stop
    async def shutdown_httpx(app: Sanic):
        await app.ctx.httpx.aclose()

    return app
