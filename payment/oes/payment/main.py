"""Main entry points."""

import os
import sys

from cattrs import Converter
from oes.payment.config import get_config
from oes.payment.service import PaymentRepo, PaymentServicesSvc, PaymentSvc
from oes.utils import configure_converter
from oes.utils.sanic import setup_app, setup_database
from sanic import Sanic


def main():
    """CLI wrapper."""
    os.execlp(
        "sanic", "oes-payment-service", "oes.payment.main.create_app", *sys.argv[1:]
    )


def create_app() -> Sanic:
    """Main app factory."""
    from oes.payment.routes import response_converter, routes

    config = get_config()
    app = Sanic("Payment")

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

    return app
