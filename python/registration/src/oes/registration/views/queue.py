"""Queue views."""
from collections.abc import Mapping, Set
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from attr import evolve
from attrs import frozen
from blacksheep import FromQuery, Response
from oes.registration.app import app
from oes.registration.checkout.service import CheckoutService
from oes.registration.database import transaction
from oes.registration.docs import docs, docs_helper
from oes.registration.models.config import Config
from oes.registration.queue.functions import add_to_queue
from oes.registration.queue.models import StationSettings
from oes.registration.queue.service import QueueService
from oes.registration.serialization import get_converter
from oes.registration.services.registration import RegistrationService
from oes.registration.util import check_not_found
from oes.util import get_now
from oes.util.blacksheep import Conflict, FromAttrs


@frozen
class StationListResponse:
    """Station list response."""

    id: str
    group_id: str


@frozen
class StationResponse:
    """Station info response."""

    id: str
    group_id: str
    settings: StationSettings


@frozen
class StationSettingsRequestBody:
    """Station settings update request."""

    open: Optional[bool] = None
    max_queue_length: Optional[int] = None
    tags: Optional[Set[str]] = None


@frozen
class AddQueueItemRequest:
    """Request body to add a queue item."""

    scan_data: Optional[str]


@frozen
class QueueItemResponse:
    """A queue item."""

    id: UUID
    date_created: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_started: Optional[datetime] = None
    duration: Optional[float] = None


@frozen
class PrintRequestResponse:
    """A print request response body."""

    id: UUID
    data: Mapping[str, Any]


@app.router.get("/stations")
@docs_helper(
    response_type=list[StationListResponse],
    response_summary="The stations",
    tags=["Queue"],
)
async def list_stations(config: Config) -> list[StationListResponse]:
    """List stations."""
    return [
        StationListResponse(id=id, group_id=cfg.group)
        for id, cfg in config.queue.stations.items()
    ]


@app.router.get("/stations/{station_id}")
@docs_helper(
    response_type=StationResponse,
    response_summary="The configuration",
    tags=["Queue"],
)
async def get_station(
    station_id: str,
    queue_service: QueueService,
) -> StationResponse:
    """Get station settings."""
    entity = check_not_found(await queue_service.get_station(station_id))

    return StationResponse(
        id=entity.id, group_id=entity.group_id, settings=entity.get_settings()
    )


@app.router.put("/stations/{station_id}")
@docs_helper(
    response_type=StationResponse,
    response_summary="The configuration",
    tags=["Queue"],
)
@transaction
async def update_station_config(
    station_id: str,
    update: FromAttrs[StationSettingsRequestBody],
    queue_service: QueueService,
    config: Config,
) -> StationResponse:
    """Update station settings."""
    station_config = check_not_found(config.queue.stations.get(station_id))
    entity = await queue_service.get_station(station_id)
    if entity is None:
        entity = await queue_service.create_station(
            station_id, group_id=station_config.group, settings=StationSettings()
        )

    await queue_service.ensure_group_exists(station_config.group)

    cur_settings = entity.get_settings()
    updated = evolve(
        cur_settings,
        open=update.value.open if update.value.open is not None else cur_settings.open,
        max_queue_length=update.value.max_queue_length
        if update.value.max_queue_length is not None
        else cur_settings.max_queue_length,
        tags=update.value.tags
        if update.value.tags is not None
        else station_config.tags,
    )
    entity.set_settings(updated)
    entity.group_id = station_config.group

    return StationResponse(id=entity.id, group_id=entity.group_id, settings=updated)


# TODO: auth
@app.router.get("/queue/{group_id}")
@docs_helper(
    response_type=list[QueueItemResponse],
    response_summary="The queue items.",
    tags=["Queue"],
)
async def get_queue_items(
    group_id: str, station_id: FromQuery[Optional[str]], queue_service: QueueService
) -> list[QueueItemResponse]:
    """Get the current queue items."""
    # TODO: group ID
    items = await queue_service.get_queue_items(group_id, station_id=station_id.value)
    results = []
    for item in items:
        data = item.get_data()
        results.append(
            QueueItemResponse(
                item.id,
                item.date_created,
                data.registration.first_name if data.registration else None,
                data.registration.last_name if data.registration else None,
                item.date_started,
                data.duration,
            )
        )

    return results


# TODO: auth
@app.router.post("/queue/{group_id}")
@docs_helper(
    response_type=QueueItemResponse,
    response_summary="The added queue item",
    tags=["Queue"],
)
@transaction
async def add_queue_item(
    group_id: str,
    scan_data: FromAttrs[AddQueueItemRequest],
    queue_service: QueueService,
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
    config: Config,
) -> QueueItemResponse:
    """Add an item to the queue."""
    queue_config = check_not_found(config.queue.groups.get(group_id))
    item = await add_to_queue(
        group_id,
        scan_data.value.scan_data,
        config=queue_config,
        queue_service=queue_service,
        checkout_service=checkout_service,
        registration_service=registration_service,
    )
    data = item.get_data()
    return QueueItemResponse(
        item.id,
        item.date_created,
        data.registration.first_name if data.registration else None,
        data.registration.last_name if data.registration else None,
        item.date_started,
        data.duration,
    )


@app.router.put("/queue/{item_id}/start")
@docs(tags=["Queue"])
@transaction
async def start_queue_item(
    item_id: UUID,
    queue_service: QueueService,
) -> Response:
    """Start a queue item."""
    item = check_not_found(await queue_service.get_queue_item(item_id, lock=True))
    if item.date_completed is not None:
        raise Conflict
    item.date_started = get_now()
    return Response(status=204)


@app.router.put("/queue/{item_id}/complete")
@docs(tags=["Queue"])
@transaction
async def complete_queue_item(
    item_id: UUID,
    queue_service: QueueService,
) -> Response:
    """Complete a queue item."""
    item = check_not_found(await queue_service.get_queue_item(item_id, lock=True))
    if item.date_completed is not None:
        raise Conflict
    item.date_completed = get_now()
    item.success = True
    return Response(status=204)


@app.router.put("/queue/{item_id}/cancel")
@docs(tags=["Queue"])
@transaction
async def cancel_queue_item(
    item_id: UUID,
    queue_service: QueueService,
) -> Response:
    """Cancel a queue item."""
    item = check_not_found(await queue_service.get_queue_item(item_id, lock=True))
    if item.date_completed is not None:
        raise Conflict
    item.date_completed = get_now()
    item.success = False
    return Response(status=204)


# TODO: auth
@app.router.get("/stations/{station_id}/print-requests")
@docs_helper(
    response_type=list[PrintRequestResponse],
    response_summary="The print request items",
    tags=["Queue"],
)
@transaction
async def get_print_requests(
    station_id: str,
    queue_service: QueueService,
) -> list[PrintRequestResponse]:
    """Get print requests for a station."""
    requests = await queue_service.get_print_requests(station_id)
    return [PrintRequestResponse(r.id, r.data) for r in requests]


# TODO: auth
@app.router.post("/stations/{station_id}/print-requests")
@docs(tags=["Queue"])
@transaction
async def create_print_request(
    station_id: str,
    registration_id: FromQuery[UUID],
    queue_service: QueueService,
    registration_service: RegistrationService,
) -> Response:
    """Create a print request."""
    reg = check_not_found(
        await registration_service.get_registration(registration_id.value)
    )
    model = reg.get_model()
    data = get_converter().unstructure(model)
    await queue_service.create_print_request(station_id, data)

    return Response(status=204)
