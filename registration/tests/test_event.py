from unittest.mock import create_autospec

import pytest
from oes.registration.event import EventStats, EventStatsRepo, EventStatsService
from oes.registration.registration import Registration
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session():
    return create_autospec(AsyncSession)


@pytest.fixture
def mock_repo():
    return create_autospec(EventStatsRepo)


@pytest.mark.asyncio
async def test_get_or_create(mock_session):
    repo = EventStatsRepo(mock_session)
    mock_session.get.return_value = None

    res = await repo.get_or_create("test")
    assert res.event_id == "test"
    assert res.next_number == 1


@pytest.mark.asyncio
async def test_assign_numbers(mock_session, mock_repo):
    stats = EventStats(event_id="test", next_number=4)
    reg1 = Registration(event_id="test")
    reg2 = Registration(event_id="test", number=3)
    reg3 = Registration(event_id="test")

    mock_repo.get_or_create.return_value = stats

    service = EventStatsService(mock_session, mock_repo)
    await service.assign_numbers("test", (reg1, reg2, reg3))
    assert reg1.number == 4
    assert reg2.number == 3
    assert reg3.number == 5
    assert stats.next_number == 6
