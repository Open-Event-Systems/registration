"""Routes."""

from cattrs import BaseValidationError
from oes.pricing.config import Config
from oes.pricing.models import PricingRequest
from oes.pricing.pricing import price_cart
from oes.pricing.serialization import converter
from sanic import BadRequest, Blueprint, HTTPResponse, Request

routes = Blueprint("pricing")


@routes.post("/price-cart")
async def price_cart_route(request: Request, config: Config) -> HTTPResponse:
    """Price a cart."""
    await request.receive_body()
    try:
        pricing_request = converter.loads(request.body, PricingRequest)
    except (ValueError, BaseValidationError):
        raise BadRequest

    result = await price_cart(config, pricing_request)
    response = HTTPResponse(converter.dumps(result), content_type="application/json")
    return response
