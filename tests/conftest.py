import os

import pytest
import pytest_asyncio
from cattrs.preconf.orjson import make_converter
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from oes.registration.orm import Base, import_entities
from oes.registration.serialization import configure_converter


@pytest_asyncio.fixture
async def engine():
    url = os.getenv("TEST_DB_URL")
    if not url:
        pytest.skip("TEST_DB_URL undefined")
    engine = create_async_engine(url)
    import_entities()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine):
    session_factory = async_sessionmaker(engine)
    yield session_factory


@pytest.fixture
def converter():
    converter = make_converter()
    configure_converter(converter)
    return converter
