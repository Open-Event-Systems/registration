"""Routes module."""

from uuid import UUID

from attrs import define
from oes.cart.cart import Cart, CartEntity, CartRegistration, CartRepo, CartService
from oes.utils.orm import transaction
from oes.utils.request import CattrsBody, raise_not_found
from oes.utils.response import ResponseConverter
from sanic import Blueprint, Request

routes = Blueprint("carts")
response_converter = ResponseConverter()


@define
class AddToCartRequestBody:
    """Request body for adding registrations to a cart."""

    registrations: list[CartRegistration]


@routes.get("/empty")
@response_converter
@transaction
async def read_empty_cart(
    request: Request, event_id: str, service: CartService
) -> CartEntity:
    """Get the empty cart."""
    cart_entity = await service.add(Cart(event_id))
    return cart_entity


@routes.get("/<cart_id>")
@response_converter
async def read_cart(
    request: Request, event_id: str, cart_id: str, repo: CartRepo
) -> CartEntity:
    """Read a cart."""
    cart_entity = await repo.get(cart_id, event_id=event_id)
    return raise_not_found(cart_entity)


@routes.post("/<cart_id>/registrations")
@response_converter
@transaction
async def add_to_cart(
    request: Request,
    event_id: str,
    cart_id: str,
    repo: CartRepo,
    service: CartService,
    body: CattrsBody,
) -> CartEntity:
    """Add a registration to a cart."""
    cart_entity = raise_not_found(await repo.get(cart_id, event_id=event_id))
    add_body = await body(AddToCartRequestBody)
    return await service.add_to_cart(cart_entity, add_body.registrations)


@routes.delete("/<cart_id>/registrations/<registration_id:uuid>")
@response_converter
@transaction
async def remove_from_cart(
    request: Request,
    event_id: str,
    cart_id: str,
    registration_id: UUID,
    repo: CartRepo,
    service: CartService,
) -> CartEntity:
    """Add a registration to a cart."""
    cart_entity = raise_not_found(await repo.get(cart_id, event_id=event_id))
    return await service.remove_from_cart(cart_entity, registration_id)
