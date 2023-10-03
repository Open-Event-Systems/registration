"""ASGI application module."""
import copy
from collections.abc import Awaitable, Callable
from http.cookiejar import Cookie, CookieJar

import httpx
from blacksheep import Application, Request, Response, Router
from cattrs.preconf.orjson import make_converter
from oes.interview.config.interview import InterviewConfig
from oes.interview.interview.types import StepConfig
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


class _NullCookieJar(CookieJar):
    def set_cookie(self, cookie: Cookie):
        return


def _make_step_config() -> StepConfig:
    converter = make_converter()
    configure_converter(converter)

    client = httpx.AsyncClient(cookies=_NullCookieJar())

    return StepConfig(
        converter=converter,
        json_default=json_default,
        http_client=client,
    )


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
    app.services.add_singleton_by_factory(_make_step_config)

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
