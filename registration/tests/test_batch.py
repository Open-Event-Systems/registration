import uuid
from unittest.mock import create_autospec

import pytest
from oes.registration.batch import BatchChangeResult, BatchChangeService, ErrorCode
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

    cur, result = await service.check("test", (change2, change1))
    assert cur == by_id
    assert result == [
        BatchChangeResult(change2, []),
        BatchChangeResult(change1, []),
    ]


@pytest.mark.asyncio
async def test_batch_check_fail(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    good = Registration(event_id="test")
    wrong_version = Registration(event_id="test", version=2)
    bad_status = Registration(event_id="test", status=Status.canceled)
    wrong_event = Registration(event_id="test2")
    change_event = Registration(event_id="test")
    wrong_multi = Registration(event_id="test2", version=2, status=Status.created)

    changes = [
        RegistrationBatchChangeFields(
            id=good.id, event_id="test", version=good.version, status=Status.created
        ),
        RegistrationBatchChangeFields(id=wrong_version.id, event_id="test", version=1),
        RegistrationBatchChangeFields(
            id=bad_status.id,
            event_id="test",
            version=bad_status.version,
            status=Status.created,
        ),
        RegistrationBatchChangeFields(
            id=wrong_event.id, event_id="test", version=wrong_event.version
        ),
        RegistrationBatchChangeFields(
            id=change_event.id, event_id="test2", version=change_event.version
        ),
        RegistrationBatchChangeFields(
            id=wrong_multi.id, event_id="test", version=1, status=Status.pending
        ),
    ]

    by_id = {
        r.id: r
        for r in reversed(
            (
                good,
                wrong_version,
                bad_status,
                wrong_event,
                change_event,
                wrong_multi,
            )
        )
    }

    def get_multi(ids, event_id, lock):
        return tuple(by_id[id] for id in ids if id in by_id)

    mock_repo.get_multi.side_effect = get_multi

    cur, results = await service.check("test", changes)

    ids_and_errors = [(res.change.id, set(res.errors)) for res in results]

    assert cur == by_id
    assert ids_and_errors == [
        (good.id, set()),
        (wrong_version.id, {ErrorCode.version}),
        (bad_status.id, {ErrorCode.status}),
        (wrong_event.id, {ErrorCode.event}),
        (change_event.id, {ErrorCode.event}),
        (wrong_multi.id, {ErrorCode.version, ErrorCode.status, ErrorCode.event}),
    ]


@pytest.mark.asyncio
async def test_batch_check_create(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version
    )
    change3 = RegistrationBatchChangeFields(id=uuid.uuid4(), event_id="test", version=2)
    change4 = RegistrationBatchChangeFields(id=uuid.uuid4(), event_id="test")

    by_id = {reg1.id: reg1}

    def get_multi(ids, event_id, lock):
        return tuple(by_id[id] for id in ids if id in by_id)

    mock_repo.get_multi.side_effect = get_multi

    cur, results = await service.check("test", (change1, change3, change4))
    assert cur == by_id
    ids_and_errors = [(res.change.id, set(res.errors)) for res in results]
    assert ids_and_errors == [
        (change1.id, set()),
        (change3.id, set()),
        (change4.id, set()),
    ]


@pytest.mark.asyncio
async def test_batch_apply(mock_session, mock_repo, mock_stats):
    service = BatchChangeService(mock_session, mock_repo, mock_stats)

    reg1 = Registration(event_id="test")

    change1 = RegistrationBatchChangeFields(
        id=reg1.id, event_id="test", version=reg1.version, email="test@test.com"
    )
    change2 = RegistrationBatchChangeFields(id=uuid.uuid4(), event_id="test", version=4)
    change3 = RegistrationBatchChangeFields(
        id=uuid.uuid4(), event_id="test", status=Status.created
    )

    updated = await service.apply("test", (change3, change1, change2), {reg1.id: reg1})
    assert len(updated) == 3
    assert reg1 in updated
    assert reg1.email == "test@test.com"
    assert any(r.id == change3.id and r.number == 2 for r in updated)
    assert [u.id for u in updated] == [change3.id, change1.id, change2.id]
