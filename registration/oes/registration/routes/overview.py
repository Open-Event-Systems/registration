"""Overview routes."""

from datetime import datetime

from attrs import frozen
from oes.registration.registration import RegistrationRepo
from oes.registration.routes.common import response_converter
from sanic import Blueprint, Request

routes = Blueprint("overview")


@frozen
class OverviewResponse:
    """Overview response body."""

    count: int


@routes.get("/overview")
@response_converter
async def get_overview(
    request: Request,
    event_id: str,
    repo: RegistrationRepo,
) -> OverviewResponse:
    """Get registration overview stats."""
    checked_in = request.args.get("checked_in")
    since = request.args.get("since")

    res = await repo.count(event_id, bool(checked_in), _parse_dt(since))
    return OverviewResponse(res)


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s).astimezone()
    except Exception:
        return None
