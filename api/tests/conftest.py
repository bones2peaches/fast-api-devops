import pytest
from httpx import AsyncClient
from app.database import engine
from app.main import app
from app.models.base import Base
import asyncio
from typing import Generator

import os

stage = os.getenv("STAGE")

from typing import List


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ],
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session")
async def start_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


@pytest.fixture(scope="session")
async def client(start_db) -> AsyncClient:

    async with AsyncClient(
        app=app,
        base_url=f"http://testserver/api/{stage.lower()}",
        headers={"Content-Type": "application/json"},
    ) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
