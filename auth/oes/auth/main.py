"""Main entry points."""

import os
import sys

from oes.auth.config import get_config
from oes.auth.service import AuthService, RefreshTokenService
from oes.utils.sanic import setup_app, setup_database
from sanic import Sanic


def main():
    """CLI wrapper."""
    os.execlp("sanic", sys.argv[0], "oes.auth.main:create_app", *sys.argv[1:])


def create_app() -> Sanic:
    """Main app entry point."""
    from oes.auth.routes import routes

    config = get_config()

    app = Sanic("Auth")
    setup_app(app, config)
    setup_database(app, config.db_url)

    app.blueprint(routes)

    app.ext.dependency(config)
    app.ext.dependency(AuthService(config))
    app.ext.add_dependency(RefreshTokenService)

    return app
