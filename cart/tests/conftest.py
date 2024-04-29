import os

import pytest
import pytest_asyncio
from oes.cart.orm import Base, import_entities
from oes.utils.sanic import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def engine():
    import_entities()
    url = os.getenv("TEST_DB_URL")
    if not url:
        pytest.skip("set TEST_DB_URL to run this test")
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine):
    session = AsyncSession(engine)
    yield session
    await session.close()
