import uuid
import pytest
from fastapi import status
from httpx import AsyncClient
from tests.integration.utils import TestUser

pytestmark = pytest.mark.anyio

user = {"username": "bigcheesehead", "password": "ilikecheeseheaders"}
bad_password_user = {"username": "bigcheesehead1", "password": "11111`"}
invalid_password_user = {"username": "bigcheesehead", "password": "ilikecheeseheader1"}
invalid_username_user = {"username": "bigcheesehead1", "password": "ilikecheeseheaders"}


@pytest.mark.parametrize(
    "payload, status_code",
    [
        (
            user,
            status.HTTP_201_CREATED,
        ),
        (
            user,
            status.HTTP_400_BAD_REQUEST,
        ),
        (invalid_username_user, status.HTTP_400_BAD_REQUEST),
    ],
)
async def test_add_user(client: AsyncClient, payload: dict, status_code: int):
    _user = TestUser(username=payload["username"], password=payload["password"])
    response = await _user.create(client=client)

    if (
        status_code == status.HTTP_400_BAD_REQUEST
        and payload["username"] == "bigcheesehead1"
    ):
        #### checking for duplicate username
        response = await _user.create(client=client)

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "login_user, status_code",
    [
        (
            user,
            status.HTTP_201_CREATED,
        ),
        (
            invalid_password_user,
            status.HTTP_400_BAD_REQUEST,
        ),
        (bad_password_user, status.HTTP_400_BAD_REQUEST),
    ],
)
async def test_user_login(client: AsyncClient, login_user, status_code: int):
    _user = TestUser(username=login_user["username"], password=login_user["password"])

    if _user.username == "bigcheesehead1":
        _user.username = "bigcheesehead"

    session = await _user.login(client=client)

    assert session.status_code == status_code


async def test_delete_session(client: AsyncClient):
    _user = TestUser(username=user["username"], password=user["password"])
    await _user.login(client=client)

    session = await _user.logout(client=client)

    assert session.status_code == status.HTTP_204_NO_CONTENT
