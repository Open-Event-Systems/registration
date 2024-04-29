"""Main entry points."""

import os
import sys

from oes.registration.batch import BatchChangeService
from oes.registration.config import get_config
from oes.registration.event import EventStatsRepo, EventStatsService
from oes.registration.registration import RegistrationService
from oes.utils.sanic import setup_app, setup_database
from sanic import Sanic


def main():
    """CLI wrapper."""
    os.execlp("sanic", sys.argv[0], "oes.registration.main:create_app", *sys.argv[1:])


def create_app() -> Sanic:
    """Main app entry point."""
    from oes.registration.registration import RegistrationRepo
    from oes.registration.routes import batch, common, registration
    from oes.registration.serialization import configure_converter

    config = get_config()

    app = Sanic("Registration")
    setup_app(app, config, common.response_converter.converter)
    setup_database(app, config.db_url)
    configure_converter(common.response_converter.converter)

    app.blueprint(registration.routes, url_prefix="/events/<event_id>/registrations")
    app.blueprint(batch.routes, url_prefix="/events/<event_id>/batch-change")

    app.ext.add_dependency(RegistrationRepo)
    app.ext.add_dependency(RegistrationService)

    app.ext.add_dependency(EventStatsRepo)
    app.ext.add_dependency(EventStatsService)

    app.ext.add_dependency(BatchChangeService)

    return app
