"""Main entry points."""

import os
import sys

import httpx
import oes.cart
import uvloop
from oes.cart.cart import (
    CartEntity,
    CartPricingService,
    CartRepo,
    CartService,
    unstructure_cart_entity,
)
from oes.cart.config import get_config
from oes.cart.routes import response_converter, routes
from oes.utils import configure_converter
from oes.utils.sanic import setup_app, setup_database
from redis.asyncio import Redis
from sanic import Request, Sanic
from sanic.worker.manager import WorkerManager

WorkerManager.THRESHOLD = 1200  # type: ignore


def main():
    """CLI wrapper."""
    os.execlp("sanic", "oes-cart-service", "oes.cart.main.create_app", *sys.argv[1:])


def create_app() -> Sanic:
    """Main app factory."""
    uvloop.install()

    config = get_config()
    app = Sanic("Cart")

    configure_converter(response_converter.converter)
    response_converter.converter.register_unstructure_hook(
        CartEntity, unstructure_cart_entity
    )

    setup_app(app, config, response_converter.converter)
    setup_database(app, config.db_url)

    app.blueprint(routes)

    app.ctx.config = config
    app.ext.dependency(config)
    app.ext.add_dependency(CartRepo)
    app.ext.add_dependency(CartService, _get_cart_service)
    app.ext.add_dependency(CartPricingService)

    @app.before_server_start
    async def setup_httpx(app: Sanic):
        app.ctx.httpx = httpx.AsyncClient()
        app.ext.dependency(app.ctx.httpx)

    @app.after_server_stop
    async def shutdown_httpx(app: Sanic):
        await app.ctx.httpx.aclose()

    @app.before_server_start
    async def setup_redis(app: Sanic):
        app.ctx.redis = Redis.from_url(config.redis_url) if config.redis_url else None
        app.ext.dependency(app.ctx.redis)

    @app.after_server_stop
    async def shutdown_redis(app: Sanic):
        redis: Redis | None = app.ctx.redis
        if redis:
            await redis.aclose()

    return app


async def _get_cart_service(request: Request, repo: CartRepo) -> CartService:
    return CartService(repo, oes.cart.__version__)
