import uuid
from unittest.mock import create_autospec

import pytest
from oes.registration.batch import BatchChangeService
from oes.registration.event import EventStats, EventStatsRepo, EventStatsService
from oes.registration.registration import (
    Registration,
    RegistrationBatchChangeFields,
    RegistrationRepo,
    Status,
)
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session():
    return create_autospec(AsyncSession)


@pytest.fixture
def mock_repo():
    return create_autospec(RegistrationRepo)


@pytest.fixture
def mock_stats(mock_session):
    repo = create_autospec(EventStatsRepo)
    repo.get_or_create.return_value = EventStats(event_id="test", next_number=2)
    stats_service = EventStatsService(mock_session, repo)

    return stats_service


@pytest.mark.asyncio
async def test_batch_check(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")
    reg2 = Registration(event_id="test", version=2)

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version
    )
    change2 = RegistrationBatchChangeFields(
        id=reg2.id, event_id="test", version=reg2.version
    )

    by_id = {reg1.id: reg1, reg2.id: reg2}

    def get_multi(ids, event_id, lock):
        return tuple(by_id[id] for id in ids if id in by_id)

    mock_repo.get_multi.side_effect = get_multi

    passed, failed = await service.check("test", (change2, change1))
    assert passed == [reg2, reg1]
    assert failed == []


@pytest.mark.asyncio
async def test_batch_check_fail(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")
    reg2 = Registration(event_id="test", version=2)

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version
    )
    change2 = RegistrationBatchChangeFields(id=reg2.id, event_id="test", version=1)

    by_id = {reg1.id: reg1, reg2.id: reg2}

    def get_multi(ids, event_id, lock):
        return tuple(by_id[id] for id in ids if id in by_id)

    mock_repo.get_multi.side_effect = get_multi

    passed, failed = await service.check("test", (change2, change1))
    assert passed == [reg1]
    assert failed == [reg2]


@pytest.mark.asyncio
async def test_batch_check_fail_invalid_status(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")
    reg2 = Registration(event_id="test", version=2, status=Status.canceled)

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version, status=Status.created
    )
    change2 = RegistrationBatchChangeFields(
        id=reg2.id, event_id="test", version=reg2.version, status=Status.created
    )

    by_id = {reg1.id: reg1, reg2.id: reg2}

    def get_multi(ids, event_id, lock):
        return tuple(by_id[id] for id in ids if id in by_id)

    mock_repo.get_multi.side_effect = get_multi

    passed, failed = await service.check("test", (change2, change1))
    assert passed == [reg1]
    assert failed == [reg2]


@pytest.mark.asyncio
async def test_batch_check_create(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")
    reg2 = Registration(event_id="test", version=2)

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version
    )
    change3 = RegistrationBatchChangeFields(event_id="test", version=2)
    change4 = RegistrationBatchChangeFields(id=uuid.uuid4(), event_id="test")

    by_id = {reg1.id: reg1, reg2.id: reg2}

    def get_multi(ids, event_id, lock):
        return tuple(by_id[id] for id in ids if id in by_id)

    mock_repo.get_multi.side_effect = get_multi

    passed, failed = await service.check("test", (change1, change3, change4))
    assert passed == [reg1]
    assert failed == []


@pytest.mark.asyncio
async def test_batch_apply(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version, email="test@test.com"
    )
    change2 = RegistrationBatchChangeFields(event_id="test", version=4)
    change3 = RegistrationBatchChangeFields(
        id=uuid.uuid4(), event_id="test", status=Status.created
    )

    updated = await service.apply("test", (change1, change2, change3), (reg1,))
    assert len(updated) == 3
    assert reg1 in updated
    assert reg1.email == "test@test.com"
    assert any(r.id == change3.id and r.number == 2 for r in updated)
