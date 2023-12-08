"""ASGI application module."""
import copy
from collections.abc import Awaitable, Callable
from http.cookiejar import Cookie, CookieJar

import httpx
from blacksheep import Application, Request, Response, Router
from oes.interview.config.interview import InterviewConfig
from oes.interview.logic import default_jinja2_env
from oes.interview.serialization import converter, json_default
from oes.interview.server.auth import APIKeyHandler, authentication, authorization
from oes.interview.server.docs import docs
from oes.interview.server.settings import Settings
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
    with set_jinja2_env(default_jinja2_env):
        return await handler(request)


class _NullCookieJar(CookieJar):
    def set_cookie(self, cookie: Cookie):
        return


def _make_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(cookies=_NullCookieJar())


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
    app.services.add_singleton_by_factory(_make_async_client)

    # middlewares
    configure_cors(
        app,
        allow_methods=("GET", "POST", "PUT", "DELETE"),
        allow_origins=settings.allowed_origins,
        allow_headers=(
            "Authorization",
            "Content-Type",
        ),
        allow_credentials=True,
    )
    app.on_middlewares_configuration(configure_forwarded_headers)

    app.middlewares.append(_set_jinja2_env)

    docs.bind_app(app)

    return app
