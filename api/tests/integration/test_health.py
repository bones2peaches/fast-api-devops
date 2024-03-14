from uuid import UUID
from fastapi import status
import pytest


async def test_health(
    client,
):

    get = await client.get("/health")

    assert get.status_code == status.HTTP_200_OK


async def test_postgres_health(
    client,
):

    get = await client.get("/health/postgres")

    assert get.status_code == status.HTTP_200_OK
