from typing import Any, Dict, Generator

import pytest
from httpx import AsyncClient, ASGITransport, Response
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ..main import app, db
from faker import Faker

fake = Faker()


@pytest.fixture(autouse=True)
def clear_db() -> Generator[None, Any, None]:
    db.clear()
    yield


@pytest.mark.asyncio
async def test_create_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        data: Dict[str, Any] = {
            "username": fake.user_name(),
            "age": fake.random_int(min=18, max=99),
        }
        response: Response = await ac.post("/users", json=data)
        assert response.status_code == 201
        res_data: Any = response.json()
        assert "id" in res_data
        assert res_data["username"] == data["username"]
        assert res_data["age"] == data["age"]


@pytest.mark.asyncio
async def test_get_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        data: Dict[str, Any] = {
            "username": fake.user_name(),
            "age": fake.random_int(min=18, max=99),
        }
        create_res: Response = await ac.post("/users", json=data)
        user_id: int = create_res.json()["id"]

        get_res: Response = await ac.get(f"/users/{user_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == user_id
        assert get_res.json()["username"] == data["username"]


@pytest.mark.asyncio
async def test_get_nonexistent_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        get_res: Response = await ac.get("/users/9999")
        assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_delete_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        data = {"username": fake.user_name(), "age": fake.random_int(min=18, max=99)}
        create_res: Response = await ac.post("/users", json=data)
        user_id: int = create_res.json()["id"]

        del_res: Response = await ac.delete(f"/users/{user_id}")
        assert del_res.status_code == 204

        get_res: Response = await ac.get(f"/users/{user_id}")
        assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_twice() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        data = {"username": fake.user_name(), "age": fake.random_int(min=18, max=99)}
        create_res: Response = await ac.post("/users", json=data)
        user_id: int = create_res.json()["id"]

        del_res: Response = await ac.delete(f"/users/{user_id}")
        assert del_res.status_code == 204

        del_res_2: Response = await ac.delete(f"/users/{user_id}")
        assert del_res_2.status_code == 404


@pytest.mark.asyncio
async def test_error_handlers() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        res: Response = await ac.get("/error_a/bad")
        assert res.status_code == 400
        assert res.json()["error"] == "Condition Not Met"

        res_b: Response = await ac.get("/error_b/0")
        assert res_b.status_code == 404
        assert res_b.json()["error"] == "Not Found"


@pytest.mark.asyncio
async def test_validation_error_handler() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        res: Response = await ac.post(
            "/validate_user",
            json={
                "username": "test",
                "age": 10,
                "email": "invalid_email",
                "password": "short",
            },
        )
        assert res.status_code == 422
        assert res.json()["error"] == "Validation Error"
