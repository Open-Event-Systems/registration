import uuid

import pytest
from oes.registration.models.event import QueueConfig
from oes.registration.models.registration import Registration, RegistrationState
from oes.registration.queue.functions import get_queue_item_data
from oes.registration.queue.models import QueueItemData
from oes.registration.serialization import get_config_converter
from oes.util import get_now

registration1 = Registration(
    id=uuid.uuid4(),
    state=RegistrationState.created,
    event_id="test",
    version=1,
    date_created=get_now(),
    option_ids={"a"},
)

registration2 = Registration(
    id=uuid.uuid4(),
    state=RegistrationState.created,
    event_id="test",
    version=1,
    date_created=get_now(),
    option_ids={"a", "b"},
)


@pytest.fixture
def config() -> QueueConfig:
    return get_config_converter().structure(
        {
            "priority": "2 if 'b' in registration.option_ids else 1",
            "tags": {
                "a": "'a' in registration.option_ids",
                "b": "'b' in registration.option_ids",
            },
            "features": {
                "a": "1 if 'a' in registration.option_ids else 0",
                "b": "1 if 'b' in registration.option_ids else 0",
                "count": "registration.option_ids | length",
            },
        },
        QueueConfig,
    )


@pytest.mark.parametrize(
    "reg, expected",
    [
        (
            registration1,
            QueueItemData(
                priority=1,
                tags=frozenset({"a"}),
                features={"a": 1, "b": 0, "count": 1},
                scan_data="test",
                registration=registration1,
            ),
        ),
        (
            registration2,
            QueueItemData(
                priority=2,
                tags=frozenset({"a", "b"}),
                features={"a": 1, "b": 1, "count": 2},
                scan_data="test",
                registration=registration2,
            ),
        ),
    ],
)
def test_get_queue_item_data(
    reg: Registration, expected: QueueItemData, config: QueueConfig
):
    res = get_queue_item_data(reg, scan_data="test", config=config)
    assert res == expected
