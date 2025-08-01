"""Main entry points."""

import os
import sys

from cattrs import Converter
from httpx import AsyncClient
from oes.payment.config import get_config
from oes.payment.mq import MQService
from oes.payment.service import PaymentRepo, PaymentServicesSvc, PaymentSvc
from oes.utils import configure_converter
from oes.utils.sanic import setup_app, setup_database
from sanic import Sanic
from sanic.worker.manager import WorkerManager

WorkerManager.THRESHOLD = 1200  # type: ignore


def main():
    """CLI wrapper."""
    os.execlp(
        "sanic",
        "oes-payment-service",
        "--single-process",
        "oes.payment.main.create_app",
        *sys.argv[1:]
    )


def create_app() -> Sanic:
    """Main app factory."""
    from oes.payment.routes import response_converter, routes

    config = get_config()
    app = Sanic("Payment", configure_logging=False)
    app.config.PROXIES_COUNT = 1

    configure_converter(response_converter.converter)

    setup_app(app, config, response_converter.converter)
    setup_database(app, config.db_url)

    app.blueprint(routes)

    app.ctx.config = config
    app.ext.dependency(config)
    app.ext.add_dependency(Converter, lambda: response_converter.converter)
    app.ext.add_dependency(PaymentRepo)
    app.ext.add_dependency(PaymentServicesSvc)
    app.ext.add_dependency(PaymentSvc)

    @app.before_server_start
    async def start_mq(app: Sanic):
        mq = MQService(config, response_converter.converter)
        app.ctx.mq = mq
        app.ext.dependency(mq)
        await mq.start()

    @app.after_server_stop
    async def stop_mq(app: Sanic):
        await app.ctx.mq.stop()

    @app.before_server_start
    async def start_httpx(app: Sanic):
        client = AsyncClient()
        app.ctx.httpx_client = client
        app.ext.dependency(client)

    @app.after_server_stop
    async def stop_httpx(app: Sanic):
        await app.ctx.httpx_client.aclose()

    return app
