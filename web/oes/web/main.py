"""Main entry points."""

import os
import sys

from cattrs.gen import make_dict_unstructure_fn
from oes.utils import configure_converter, setup_logging
from oes.utils.sanic import setup_app
from oes.web.config import get_config
from oes.web.routes.common import response_converter
from oes.web.routes.registration import RegistrationService
from sanic import Sanic


def main():
    """CLI wrapper."""
    os.execlp("sanic", "oes-web-service", "oes.web.main.create_app", *sys.argv[1:])


def create_app() -> Sanic:
    """Main app factory."""
    from oes.web.routes import event, selfservice

    config = get_config()
    app = Sanic("Web", configure_logging=False)
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
    # setup_database(app, config.db_url)

    app.blueprint(event.routes)
    app.blueprint(selfservice.routes)

    app.ctx.config = config
    app.ext.dependency(config)
    app.ext.add_dependency(RegistrationService)

    @app.before_server_start
    async def setup_log(app: Sanic):
        setup_logging(app.debug)

    return app
