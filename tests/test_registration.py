import pytest
from cattrs import Converter
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from oes.registration.registration import (
    Registration,
    RegistrationCreate,
    RegistrationRepo,
    RegistrationUpdate,
    Status,
)


def test_serialize_registration(converter: Converter):
    reg = Registration(event_id="test", extra_data={"test": 123})
    data = converter.unstructure(reg)
    assert data == {
        "id": reg.id,
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

        update = converter.structure(data, RegistrationUpdate)
        assert update.email == "test@test.com"
        assert update.extra_data == {"extra": True}

        reg = await repo.get(id)
        assert reg
        update.apply(reg)
        await repo.flush()
        assert reg.email == "test@test.com"
        assert reg.status == Status.pending
        assert reg.extra_data == {"extra": True}
        assert reg.event_id == "test"
        assert reg.version == 2


def test_create(converter: Converter):
    data = {
        "id": "ignore",
        "event_id": "test",
        "status": "created",
        "first_name": "first",
        "last_name": "last",
        "email": "test@test.com",
        "extra": 123,
    }
    create_obj = converter.structure(data, RegistrationCreate)
    reg = create_obj.create()
    assert reg.id != "ignore"
    assert reg.event_id == "test"
    assert reg.status == Status.created
    assert reg.first_name == "first"
    assert reg.last_name == "last"
    assert reg.email == "test@test.com"
    assert reg.extra_data == {"extra": 123}