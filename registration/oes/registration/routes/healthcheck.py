"""Health check routes."""

from oes.registration.mq import MQService
from oes.registration.registration import RegistrationRepo
from sanic import Blueprint, HTTPResponse, Request

routes = Blueprint("access_code")


@routes.get("/_healthcheck")
async def healthcheck(
    request: Request, repo: RegistrationRepo, message_queue: MQService
) -> HTTPResponse:
    """Health check endpoint."""
    await repo.get("")
    if not message_queue.ready:
        return HTTPResponse(status=503)
    return HTTPResponse(status=204)
