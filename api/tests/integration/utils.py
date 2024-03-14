from httpx import AsyncClient


class TestUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    async def create(self, client: AsyncClient):
        response = await client.post(
            "/user",
            json={"username": self.username, "password": self.password},
        )

        return response

    async def login(self, client: AsyncClient):
        response = await client.post(
            "/user/session",
            json={"username": self.username, "password": self.password},
        )
        if response.status_code == 201:
            self.token = response.json()["access_token"]

        return response

    async def logout(self, client: AsyncClient):
        response = await client.delete(
            "/user/session",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        return response
