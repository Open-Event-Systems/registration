"""Queue views."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from attrs import frozen
from oes.registration.app import app
from oes.registration.docs import docs_helper
from oes.registration.queue.service import QueueService


@frozen
class QueueItemResponse:
    id: UUID
    date_created: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_started: Optional[datetime] = None
    duration: Optional[float] = None


# TODO: auth
@app.router.get("/queue")
@docs_helper(
    response_type=list[QueueItemResponse],
    response_summary="The queue items.",
    tags=["Queue"],
)
async def get_queue_items(queue_service: QueueService) -> list[QueueItemResponse]:
    """Get the current queue items."""
    items = await queue_service.get_queue_items()
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
