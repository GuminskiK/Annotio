
import json

import pytest

from src.app.core.config import settings
from tests.conftest import TEST_USER_PASSWORD, TEST_USER_USERNAME


@pytest.mark.asyncio
async def test_login_ok(client, user, fake_redis):
    response = client.post(
        "/auth/login",
        data={"username": TEST_USER_USERNAME, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Logged in successfully!"

    session_id = response.cookies.get(settings.SESSION_COOKIE_NAME)
    assert session_id is not None

    session_key = f"session:{session_id}"
    assert session_key in fake_redis.data
    session_data = json.loads(fake_redis.data[session_key])

    assert session_data["session_id"] == session_id
    assert session_data["user_id"] == str(user.id)
    assert session_data["username"] == TEST_USER_USERNAME
    assert session_data["remember_me"] is False
    assert fake_redis.expires[session_key] == settings.SESSION_TTL

    user_sessions_key = f"user_session:{user.id}"
    assert session_id in fake_redis.data[user_sessions_key]

@pytest.mark.asyncio
async def test_login_no_username(client, user, fake_redis):
    response = client.post(
        "/auth/login",
        data={"password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 401
    assert not fake_redis.data

@pytest.mark.asyncio
async def test_login_no_password(client, user, fake_redis):
    response = client.post(
        "/auth/login",
        data={"username": TEST_USER_USERNAME},
    )
    assert response.status_code == 401
    assert not fake_redis.data

@pytest.mark.asyncio
async def test_login_bad_password(client, user, fake_redis):
    response = client.post(
        "/auth/login",
        data={"username": TEST_USER_USERNAME, "password": "wrong"},
    )
    assert response.status_code == 401
    assert not fake_redis.data

@pytest.mark.asyncio
async def test_logout(client, user, fake_redis):
    response = client.post(
        "/auth/login",
        data={"username": TEST_USER_USERNAME, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200

    session_id = response.cookies.get(settings.SESSION_COOKIE_NAME)
    assert session_id is not None

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logged out successfully!"

    session_key = f"session:{session_id}"
    assert session_key not in fake_redis.data