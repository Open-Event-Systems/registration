"""Event routes."""

from datetime import date as dt_date

from attrs import frozen
from oes.utils.request import raise_not_found
from oes.web.config import Config, Event
from oes.web.routes.common import response_converter
from sanic import Blueprint, Request

routes = Blueprint("events")


@frozen
class EventResponse:
    """Event response object."""

    id: str
    date: dt_date
    title: str | None = None
    description: str | None = None
    open: bool = False
    visible: bool = False


@routes.get("/events")
@response_converter(list[EventResponse])
async def list_events(request: Request, config: Config) -> list[Event]:
    """List events."""
    return sorted(config.events, key=lambda e: e.date, reverse=True)


@routes.get("/events/<event_id>")
@response_converter(EventResponse)
async def read_event(request: Request, event_id: str, config: Config) -> Event:
    """Read an event."""
    event = next((e for e in config.events if e.id == event_id), None)
    return raise_not_found(event)
