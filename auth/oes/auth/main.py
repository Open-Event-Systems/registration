"""Main entry points."""

import os
import sys

from oes.auth.config import get_config
from oes.auth.email import EmailAuthRepo, EmailAuthService
from oes.auth.mq import MQService
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
    app.ext.add_dependency(EmailAuthRepo)
    app.ext.add_dependency(EmailAuthService)

    @app.before_server_start
    async def start_mq(app: Sanic):
        mq = MQService(config)
        app.ctx.mq = mq
        app.ext.dependency(mq)
        await mq.start()

    @app.after_server_stop
    async def stop_mq(app: Sanic):
        await app.ctx.mq.stop()

    return app
