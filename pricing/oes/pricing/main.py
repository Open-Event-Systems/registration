"""Main entry points."""

import os
import sys

from oes.pricing.config import get_config
from oes.pricing.serialization import converter
from oes.utils.sanic import setup_app
from sanic import Sanic


def main():
    """CLI wrapper."""
    os.execlp(
        "sanic", "oes-pricing-service", "oes.pricing.main:create_app", *sys.argv[1:]
    )


def create_app():
    """Get the web app."""
    from oes.pricing.routes import routes

    config = get_config()

    app = Sanic("Pricing")
    setup_app(app, config, converter)
    app.blueprint(routes)

    app.ext.dependency(config)

    return app
