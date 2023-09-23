"""ASGI application module."""
import copy
from collections.abc import Awaitable, Callable

from blacksheep import Application, Request, Response, Router
from oes.interview.config.interview import InterviewConfig
from oes.interview.interview.step import HookStep
from oes.interview.serialization import configure_converter, converter, json_default
from oes.interview.server.auth import APIKeyHandler, authentication, authorization
from oes.interview.server.docs import docs
from oes.interview.server.settings import Settings
from oes.interview.variables.env import jinja2_env
from oes.template import set_jinja2_env
from oes.util.blacksheep import (
    AttrsBinder,
    JSONResponseFunc,
    configure_cors,
    configure_forwarded_headers,
)

router = Router()
"""The router."""

json_response = JSONResponseFunc(default=json_default)
"""JSON response function."""

AttrsBinder.cattrs_converter = converter


async def _set_jinja2_env(
    request: Request, handler: Callable[[Request], Awaitable[Response]]
) -> Response:
    with set_jinja2_env(jinja2_env):
        return await handler(request)


def make_app(settings: Settings, interview_config: InterviewConfig) -> Application:
    """Return the ASGI app."""
    import oes.interview.server.views  # noqa

    router_copy = copy.deepcopy(router)

    app = Application(router=router_copy)

    # auth
    authentication.add(
        APIKeyHandler(
            settings.api_key,
        )
    )

    app.use_authentication(authentication)
    app.use_authorization(authorization)

    # services

    app.services.add_instance(settings)
    app.services.add_instance(interview_config)

    configure_converter(HookStep.converter)
    HookStep.json_default = json_default

    # middlewares
    configure_cors(
        app,
        allow_origins=settings.allowed_origins,
        allow_headers=(
            "Authorization",
            "Content-Type",
        ),
    )
    app.on_middlewares_configuration(configure_forwarded_headers)

    app.middlewares.append(_set_jinja2_env)

    docs.bind_app(app)

    return app
