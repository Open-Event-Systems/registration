"""Queue functions."""
import re
from typing import Optional, cast

from oes.registration.checkout.service import CheckoutService
from oes.registration.models.event import QueueConfig
from oes.registration.models.registration import Registration
from oes.registration.queue.models import QueueItemData
from oes.registration.serialization import get_converter
from oes.template import evaluate


def get_queue_item_data(
    registration: Registration,
    /,
    *,
    scan_data: Optional[str] = None,
    config: QueueConfig,
) -> QueueItemData:
    """Get a :class:`QueueItemData` for a registration."""
    priority = get_priority(registration, config=config)
    features = get_features(registration, config=config)
    tags = get_tags(registration, config=config)
    return QueueItemData(
        priority=priority,
        tags=tags,
        features=features,
        registration=registration,
        scan_data=scan_data,
    )


def get_priority(registration: Registration, /, *, config: QueueConfig) -> int:
    """Get the priority for a registration."""
    context = {"registration": get_converter().unstructure(registration)}
    return cast(int, evaluate(config.priority, context))


def get_features(
    registration: Registration,
    /,
    *,
    config: QueueConfig,
) -> dict[str, float]:
    """Get the features and scores for a registration."""
    context = {"registration": get_converter().unstructure(registration)}
    return {
        feature: cast(float, evaluate(score, context))
        for feature, score in config.features.items()
    }


def get_tags(
    registration: Registration,
    /,
    *,
    config: QueueConfig,
) -> frozenset[str]:
    """Get the tags for a registration."""
    context = {"registration": get_converter().unstructure(registration)}
    return frozenset(
        tag for tag, when in config.tags.items() if evaluate(when, context)
    )


def _parse_receipt_url(url: str) -> tuple[str, int]:
    match = re.match(r"/([a-z0-9]+)(?:#r([0-9]+))?$", url, re.I)
    if not match:
        return "", 0
    elif match.group(2):
        return match.group(1), int(match.group(2)) - 1
    else:
        return match.group(1), 0


async def _get_reg_id_by_receipt(receipt_id: str, index: int, service: CheckoutService):
    checkout = await service.get_checkout_by_receipt_id(receipt_id)
    if not checkout:
        return None
    cart_data = checkout.get_cart_data()
    try:
        return cart_data.registrations[index].id
    except IndexError:
        return None
