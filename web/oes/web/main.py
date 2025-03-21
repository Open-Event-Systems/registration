"""Main entry points."""

import os
import sys

import httpx
from cattrs.gen import make_dict_unstructure_fn
from oes.utils import configure_converter, setup_logging
from oes.utils.sanic import setup_app
from oes.web.config import get_config
from oes.web.routes.common import response_converter
from sanic import Sanic
from sanic.worker.manager import WorkerManager

WorkerManager.THRESHOLD = 1200  # type: ignore


def main():
    """CLI wrapper."""
    os.execlp(
        "sanic",
        "oes-web-service",
        "--single-process",
        "oes.web.main.create_app",
        *sys.argv[1:]
    )


def create_app() -> Sanic:
    """Main app factory."""
    from oes.web.access_code import AccessCodeService
    from oes.web.cart import CartService
    from oes.web.interview import InterviewService
    from oes.web.payment import PaymentService
    from oes.web.registration import RegistrationService
    from oes.web.routes import admin, cart, event, payment, registration, selfservice
    from oes.web.selfservice import SelfServiceService

    config = get_config()
    app = Sanic("Web", configure_logging=False)
    app.config.PROXIES_COUNT = 1
    setup_logging()

    configure_converter(response_converter.converter)
    response_converter.converter.register_unstructure_hook(
        selfservice.SelfServiceRegistration,
        make_dict_unstructure_fn(
            selfservice.SelfServiceRegistration,
            response_converter.converter,
            _cattrs_omit_if_default=True,
        ),
    )

    setup_app(app, config, response_converter.converter)

    app.blueprint(event.routes)
    app.blueprint(cart.routes)
    app.blueprint(payment.routes)
    app.blueprint(registration.routes)
    app.blueprint(selfservice.routes)
    app.blueprint(admin.routes)

    app.ctx.config = config
    app.ext.dependency(config)
    app.ext.add_dependency(RegistrationService)
    app.ext.add_dependency(InterviewService)
    app.ext.add_dependency(CartService)
    app.ext.add_dependency(PaymentService)
    app.ext.add_dependency(AccessCodeService)
    app.ext.add_dependency(SelfServiceService)

    @app.before_server_start
    async def setup_log(app: Sanic):
        setup_logging(app.debug)

    @app.before_server_start
    async def setup_httpx(app: Sanic):
        client = httpx.AsyncClient()
        app.ctx.httpx = client
        app.ext.dependency(client)

    @app.after_server_stop
    async def shutdown_httpx(app: Sanic):
        await app.ctx.httpx.aclose()

    return app
