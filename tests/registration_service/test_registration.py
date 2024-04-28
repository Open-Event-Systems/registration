import uuid
from unittest.mock import create_autospec

import pytest
from cattrs import Converter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from oes.registration_service.registration import (
    ConflictError,
    Registration,
    RegistrationCreateFields,
    RegistrationRepo,
    RegistrationService,
    RegistrationUpdateFields,
    Status,
    StatusError,
)


@pytest.fixture
def mock_session():
    return create_autospec(AsyncSession)


@pytest.fixture
def mock_repo():
    return create_autospec(RegistrationRepo)


def test_serialize_registration(converter: Converter):
    reg = Registration(event_id="test", extra_data={"test": 123})
    data = converter.unstructure(reg)
    assert data == {
        "id": str(reg.id),
        "status": Status.pending,
        "version": 1,
        "event_id": "test",
        "date_created": reg.date_created.isoformat(),
        "test": 123,
    }
    from_data = converter.structure(data, Registration)
    assert from_data == reg


@pytest.mark.asyncio
async def test_update_version(session_factory: async_sessionmaker):
    async with session_factory() as session:
        repo = RegistrationRepo(session)
        reg = Registration(event_id="test")
        id = reg.id
        repo.add(reg)
        await session.flush()
        assert reg.version == 1
        await session.commit()

        reg = await repo.get(id)
        assert reg
        reg.email = "test@test.com"
        assert reg.version == 1
        await session.flush()
        assert reg.version == 2
        assert reg.date_updated


@pytest.mark.asyncio
async def test_check_version(session_factory: async_sessionmaker, converter: Converter):
    async with session_factory() as session:
        repo = RegistrationRepo(session)
        reg = Registration(event_id="test")

        copy1 = converter.structure(converter.unstructure(reg), Registration)
        copy2 = converter.structure(converter.unstructure(reg), Registration)

        repo.add(reg)
        await session.commit()

        copy1.email = "test@test.com"
        copy1 = await repo.merge(copy1)
        await session.flush()
        assert copy1.date_updated
        assert copy1.version == 2

        copy2.last_name = "test"
        with pytest.raises(StaleDataError):
            await repo.merge(copy2)


@pytest.mark.asyncio
async def test_updatable_fields(
    session_factory: async_sessionmaker, converter: Converter
):
    async with session_factory() as session:
        repo = RegistrationRepo(session)
        reg = Registration(event_id="test")
        id = reg.id

        data = converter.unstructure(reg)

        repo.add(reg)
        await session.commit()

        data["id"] = id
        data["event_id"] = "other"
        data["version"] = 1
        data["status"] = Status.canceled
        data["email"] = "test@test.com"
        data["extra"] = True

        update = converter.structure(data, RegistrationUpdateFields)
        assert update.email == "test@test.com"
        assert update.extra_data == {"extra": True}

        reg = await repo.get(id)
        assert reg
        update.apply(reg)
        await repo.session.flush()
        assert reg.email == "test@test.com"
        assert reg.status == Status.pending
        assert reg.extra_data == {"extra": True}
        assert reg.event_id == "test"
        assert reg.version == 2


def test_create(converter: Converter):
    data = {
        "id": "ignore",
        "event_id": "test-other",
        "status": "created",
        "first_name": "first",
        "last_name": "last",
        "email": "test@test.com",
        "extra": 123,
    }
    create_obj = converter.structure(data, RegistrationCreateFields)
    reg = create_obj.create("test")
    assert reg.id != "ignore"
    assert reg.event_id == "test"
    assert reg.status == Status.created
    assert reg.first_name == "first"
    assert reg.last_name == "last"
    assert reg.email == "test@test.com"
    assert reg.extra_data == {"extra": 123}


def test_complete_cancel():
    reg = Registration(event_id="test")
    assert reg.complete() is True
    assert reg.status == Status.created
    assert reg.complete() is False

    assert reg.cancel() is True
    assert reg.cancel() is False
    with pytest.raises(StatusError):
        reg.complete()


@pytest.mark.asyncio
async def test_get_multi(session_factory: async_sessionmaker):
    async with session_factory() as session:
        repo = RegistrationRepo(session)
        regs = [Registration(event_id="test") for _ in range(3)]
        ids = [r.id for r in regs] + [uuid.uuid4()]

        for reg in regs:
            repo.add(reg)

        repo.add(Registration(event_id="other"))

        await session.flush()

        res = await repo.get_multi(ids, event_id="test", lock=True)
        assert len(res) == 3
        assert all(r in res for r in regs)
        assert sorted(r.id for r in regs) == [r.id for r in res]


@pytest.mark.asyncio
async def test_service_create(mock_repo, mock_session):
    service = RegistrationService(mock_session, mock_repo)
    reg = await service.create("test", RegistrationCreateFields(email="test@test.com"))
    assert reg.event_id == "test"
    assert reg.email == "test@test.com"
    mock_repo.add.assert_called_with(reg)


@pytest.mark.asyncio
async def test_service_update(mock_repo, mock_session):
    cur = Registration(event_id="test", email="test@test.com")
    mock_repo.get.return_value = cur

    service = RegistrationService(mock_session, mock_repo)

    update = RegistrationUpdateFields(version=cur.version, email="other@test.com")

    cur_id = cur.id
    updated = await service.update("test", cur.id, update)
    assert updated
    assert updated.id == cur_id
    assert updated.email == "other@test.com"
    # version change happens on flush...


@pytest.mark.asyncio
async def test_service_update_etag(mock_repo, mock_session):
    cur = Registration(event_id="test", email="test@test.com")
    mock_repo.get.return_value = cur

    service = RegistrationService(mock_session, mock_repo)

    update = RegistrationUpdateFields(email="other@test.com")

    cur_id = cur.id
    cur_etag = service.get_etag(cur)
    updated = await service.update("test", cur.id, update, etag=cur_etag)
    assert updated
    assert updated.id == cur_id
    assert updated.email == "other@test.com"
    # version change happens on flush...


@pytest.mark.asyncio
async def test_service_update_conflict(mock_repo, mock_session):
    cur = Registration(event_id="test", email="test@test.com")
    mock_repo.get.return_value = cur

    service = RegistrationService(mock_session, mock_repo)

    update = RegistrationUpdateFields(version=3, email="other@test.com")

    with pytest.raises(ConflictError):
        await service.update("test", cur.id, update)


@pytest.mark.asyncio
async def test_service_update_conflict_etag(mock_repo, mock_session):
    cur = Registration(event_id="test", email="test@test.com")
    mock_repo.get.return_value = cur

    service = RegistrationService(mock_session, mock_repo)

    update = RegistrationUpdateFields(email="other@test.com")

    with pytest.raises(ConflictError):
        await service.update("test", cur.id, update, etag='W/"3"')


@pytest.mark.asyncio
async def test_service_update_not_found(mock_repo, mock_session):
    cur = Registration(event_id="test", email="test@test.com")
    mock_repo.get.return_value = None

    service = RegistrationService(mock_session, mock_repo)

    update = RegistrationUpdateFields(version=cur.version, email="other@test.com")

    updated = await service.update("test", cur.id, update)
    assert updated is None
