"""Main entry points."""

import os
import sys

import oes.cart
import uvloop
from oes.cart.cart import CartEntity, CartRepo, CartService, unstructure_cart_entity
from oes.cart.config import get_config
from oes.cart.routes import response_converter, routes
from oes.utils import configure_converter
from oes.utils.sanic import setup_app, setup_database
from sanic import Request, Sanic


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

    app.blueprint(routes, url_prefix="/events/<event_id>/carts")

    app.ctx.config = config
    app.ctx.salt = config.salt.encode()

    app.ext.add_dependency(CartRepo)
    app.ext.add_dependency(CartService, _get_cart_service)

    return app


async def _get_cart_service(request: Request, repo: CartRepo) -> CartService:
    return CartService(repo, request.app.ctx.salt, oes.cart.__version__)
