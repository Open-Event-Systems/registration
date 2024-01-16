"""Queue functions."""
import asyncio
import re
import uuid
from collections.abc import Iterable, Mapping, Set
from typing import Optional, cast
from uuid import UUID

from attrs import evolve
from oes.registration.checkout.service import CheckoutService
from oes.registration.entities.registration import RegistrationEntity
from oes.registration.models.config import QueueConfig, QueueGroupConfig
from oes.registration.models.registration import Registration
from oes.registration.queue.entities import QueueItemEntity, StationEntity
from oes.registration.queue.models import QueueItemData
from oes.registration.queue.service import QueueService
from oes.registration.queue.solver import (
    QueueItemInfo,
    StationInfo,
    solve_features,
    solve_queue,
)
from oes.registration.serialization import get_converter
from oes.registration.services.registration import RegistrationService
from oes.template import evaluate
from sqlalchemy import func, null, or_, select


async def add_to_queue(
    group_id: str,
    scan_data: Optional[str] = None,
    /,
    *,
    config: QueueGroupConfig,
    queue_service: QueueService,
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
) -> QueueItemEntity:
    """Add an item to the queue."""
    queue_item = await make_queue_item(
        group_id,
        scan_data,
        config=config,
        checkout_service=checkout_service,
        registration_service=registration_service,
    )
    return await queue_service.save_queue_item(queue_item)


async def make_queue_item(
    group_id: str,
    scan_data: Optional[str] = None,
    /,
    *,
    config: QueueGroupConfig,
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
) -> QueueItemEntity:
    """Make a :class:`QueueItemEntity` from scan data.

    Args:
        group_id: The group ID.
        scan_data: The scanned data.
        config: The checkout config.
        checkout_service: The checkout service.
        registration_service: The registration service.
    """
    reg = await _parse_scan_data(scan_data, checkout_service, registration_service)

    if reg:
        item_data = get_queue_item_data(
            reg.get_model(), scan_data=scan_data, config=config
        )
    else:
        if scan_data and scan_data.startswith("tags:"):
            tags = _parse_tags_url(scan_data)
            features = {t: 1 for t in tags}
            item_data = QueueItemData(scan_data=scan_data, tags=tags, features=features)
        else:
            item_data = QueueItemData(scan_data=scan_data)

    entity = QueueItemEntity(
        id=uuid.uuid4(),
        group_id=group_id,
    )
    entity.set_data(item_data)
    return entity


async def _parse_scan_data(
    scan_data: Optional[str],
    checkout_service: CheckoutService,
    registration_service: RegistrationService,
) -> Optional[RegistrationEntity]:
    if scan_data:
        if scan_data.lower().startswith("http:") or scan_data.lower().startswith(
            "https:"
        ):
            receipt_id, index = _parse_receipt_url(scan_data)
            return await _get_reg_by_receipt_id(
                receipt_id, index, checkout_service, registration_service
            )
        elif scan_data.startswith("@"):
            id_data = _parse_id(scan_data)
            return await _get_reg_by_id_data(id_data, registration_service)

    return None


def _parse_id(data: str) -> dict[str, str]:
    values = {}

    entries = re.finditer(r"^D([A-Z]{2})(.*)$", data, re.M)
    for match in entries:
        key = match.group(1)
        value = match.group(2)

        if key == "AC":
            values["first_name"] = value
        elif key == "CS":
            values["last_name"] = value
        elif key == "BB":
            mm = value[0:2]

            if int(mm) > 12:
                mm = value[4:6]
                dd = value[6:8]
                yyyy = value[0:4]
            else:
                dd = value[2:4]
                yyyy = value[4:8]
            values["birth_date"] = f"{yyyy}-{mm}-{dd}"

    return values


def _parse_tags_url(data: str) -> Set[str]:
    _, _, tags = data.partition("tags:")
    return frozenset(t.strip() for t in tags.split(","))


async def _get_reg_by_id_data(
    data: Mapping[str, str],
    registration_service: RegistrationService,
) -> Optional[RegistrationEntity]:
    if "first_name" not in data or "last_name" not in data:
        return None

    db = registration_service.db
    q = select(RegistrationEntity).where(
        func.lower(RegistrationEntity.first_name) == data["first_name"].lower(),
        func.lower(RegistrationEntity.last_name) == data["last_name"].lower(),
    )

    if "birth_date" in data:
        q = q.where(
            or_(
                RegistrationEntity.extra_data.contains(
                    {"birth_date": data["birth_date"]}
                ),
                RegistrationEntity.extra_data["birth_date"].as_string() == null(),
            )
        )

    res = await db.execute(q)

    return res.scalar()


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
    config: QueueGroupConfig,
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


def get_priority(registration: Registration, /, *, config: QueueGroupConfig) -> int:
    """Get the priority for a registration."""
    context = {"registration": get_converter().unstructure(registration)}
    return cast(int, evaluate(config.priority, context))


def get_features(
    registration: Registration,
    /,
    *,
    config: QueueGroupConfig,
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
    config: QueueGroupConfig,
) -> frozenset[str]:
    """Get the tags for a registration."""
    context = {"registration": get_converter().unstructure(registration)}
    return frozenset(
        tag for tag, when in config.tags.items() if evaluate(when, context)
    )


async def compute_station_stats(
    station: StationEntity, /, *, config: QueueGroupConfig, queue_service: QueueService
):
    """Update a :class:`StationEntity` with stats from recent check-ins."""
    stats = await queue_service.get_queue_stats(station.id)
    features = list(config.features.keys())
    intercept, coefs = await asyncio.to_thread(solve_features, features, stats)
    data = station.get_settings()
    data = evolve(data, feature_intercept=intercept, feature_coefficients=coefs)
    station.set_settings(data)


def _parse_receipt_url(url: str) -> tuple[str, int]:
    match = re.search(r"/([a-z0-9]+)(?:#r([0-9]+))?$", url, re.I)
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


async def solve(
    config: QueueConfig,
    group_id: str,
    queue_service: QueueService,
) -> dict[UUID, QueueItemEntity]:
    """Solve queue assignments."""
    await queue_service.get_group(group_id, lock=True)
    group_config = config.groups[group_id]
    features = list(group_config.features.keys())
    stations = await _get_stations(group_id, config, queue_service)

    queue_items = await _get_queue_items(group_id, queue_service)
    item_info = _get_queue_item_info(queue_items.values())
    station_info = {
        s.id: await _get_station_info(queue_items, s) for s in stations.values()
    }

    to_solve = {
        it.id: it for it in item_info.values() if queue_items[it.id].station_id is None
    }

    res = await asyncio.to_thread(
        solve_queue, features, list(station_info.values()), list(to_solve.values())
    )
    for id, assignment in res.items():
        # Set station_id it was assigned to
        item = queue_items[id]
        item.station_id = assignment

        # set predicted service duration
        station = station_info[assignment]
        info = item_info[id]
        duration = info.get_service_time(station)
        item_data = item.get_data()
        updated_data = evolve(item_data, duration=duration)
        item.set_data(updated_data)

    # increase priority of all passed-over items
    for item in queue_items.values():
        if item.id not in res:
            item_data = item.get_data()
            updated_data = evolve(item_data, priority=item_data.priority + 1)
            item.set_data(updated_data)

    return queue_items


async def _get_stations(
    group_id: str, config: QueueConfig, queue_service: QueueService
) -> dict[str, StationEntity]:
    entities = {}
    for station_id, station_config in config.stations.items():
        if station_config.group == group_id:
            station_entity = await queue_service.get_station(station_id)
            settings = station_entity.get_settings()
            if not settings.open:
                continue
            entities[station_entity.id] = station_entity
    return entities


async def _get_station_info(
    queue_items: Mapping[UUID, QueueItemEntity], station_entity: StationEntity
) -> StationInfo:
    settings = station_entity.get_settings()
    queue_items = [
        it for it in queue_items.values() if it.station_id == station_entity.id
    ]
    n_slots = max(settings.max_queue_length - len(queue_items), 0)
    wait_time = sum(it.get_data().duration or 0 for it in queue_items)
    return StationInfo(
        id=station_entity.id,
        slots=n_slots,
        intercept=settings.feature_intercept,
        coefs=settings.feature_coefficients,
        wait_time=wait_time,
        tags=settings.tags,
    )


async def _get_queue_items(
    group_id: str, queue_service: QueueService
) -> dict[UUID, QueueItemEntity]:
    items = await queue_service.get_queue_items(group_id, lock=True)
    return {it.id: it for it in items}


def _get_queue_item_info(
    queue_items: Iterable[QueueItemEntity],
) -> dict[UUID, QueueItemInfo]:
    results = {}
    for item in queue_items:
        item_data = item.get_data()
        results[item.id] = QueueItemInfo(
            id=item.id,
            priority=item_data.priority,
            tags=item_data.tags,
            features=item_data.features,
        )
    return results
