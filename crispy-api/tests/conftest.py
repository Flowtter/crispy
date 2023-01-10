import asyncio

import pytest
from httpx import AsyncClient
from mongo_thingy import AsyncThingy

from api import app, init_database


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="https://tests") as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def database():
    await init_database()

    database = AsyncThingy.database
    assert "test" in database.name
    return database


@pytest.fixture(autouse=True, scope="session")
async def clean_database(database):
    for collection_name in await database.list_collection_names():
        collection = database[collection_name]
        await collection.delete_many({})
