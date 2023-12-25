"""Queue functions."""
import re
import uuid
from typing import Optional, cast

from oes.registration.checkout.service import CheckoutService
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.models.event import QueueConfig
from oes.registration.models.registration import Registration
from oes.registration.queue.entities import QueueItemEntity
from oes.registration.queue.models import QueueItemData
from oes.registration.serialization import get_converter
from oes.registration.services.registration import RegistrationService
from oes.template import evaluate


async def make_queue_item(
    scan_data: Optional[str] = None,
    /,
    *,
    config: QueueConfig,
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
) -> QueueItemEntity:
    """Make a :class:`QueueItemEntity` from scan data.

    Args:
        scan_data: The scanned data.
        config: The checkout config.
        checkout_service: The checkout service.
        registration_service: The registration service.
    """
    reg = await _parse_scan_data(scan_data, checkout_service, registration_service)

    # TODO: ID parsing

    if reg:
        item_data = get_queue_item_data(
            reg.get_model(), scan_data=scan_data, config=config
        )
    else:
        item_data = QueueItemData(scan_data=scan_data)

    entity = QueueItemEntity(
        id=uuid.uuid4(),
    )
    entity.set_data(item_data)
    return entity


async def _parse_scan_data(
    scan_data: Optional[str],
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
) -> Optional[RegistrationEntity]:
    if scan_data and (scan_data.startswith("http:") or scan_data.startswith("https:")):
        receipt_id, index = _parse_receipt_url(scan_data)
        return await _get_reg_by_receipt_id(
            receipt_id, index, checkout_service, registration_service
        )
    return None


async def _get_reg_by_receipt_id(
    receipt_id: str,
    index: int,
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
) -> Optional[RegistrationEntity]:
    if receipt_id:
        reg_id = await _get_reg_id_by_receipt(receipt_id, index, checkout_service)
        if reg_id:
            return await registration_service.get_registration(reg_id)
    return None


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
