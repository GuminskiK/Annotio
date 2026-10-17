import uuid
import pytest
from sqlmodel import select
import re
from src.app.modules.auth.utils.jwt import create_token
from src.app.modules.auth.models.Tokens import TokenTypes
from datetime import timedelta
from src.app.modules.auth.models.Users import User
from src.app.modules.auth.utils.auth_utils import verify_password
from tests.conftest import TEST_USER_USERNAME, TEST_USER_EMAIL, TEST_USER_PASSWORD

def assert_is_uuid4(value: str):
  
  assert isinstance(value, str), f"Expected string, got {type(value)}"
  try:
    parsed = uuid.UUID(value, version=4)
    assert str(parsed) == value.lower()
  except ValueError:
    pytest.fail(f"'{value}' is not a valid UUID version 4")

@pytest.mark.asyncio
async def test_post_good(client, db_session):
    
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": TEST_USER_PASSWORD}
    )

    assert response.status_code == 201
    data = response.json()

    assert data["username"] == TEST_USER_USERNAME
    assert data["email"] == TEST_USER_EMAIL
    assert_is_uuid4(data["id"])

    assert data["roles"] == ["worker"]
    assert data["is_activated"] is False
    assert data["is_totp_enabled"] is False
    assert data["is_superuser"] is False

    result = await db_session.exec(
        select(User).where(User.username == TEST_USER_USERNAME)
    )
    user = result.one()

    assert user.hashed_password != TEST_USER_PASSWORD
    assert verify_password(TEST_USER_PASSWORD, user.hashed_password)
    assert not verify_password("WrongPassword1!", user.hashed_password)

def test_post_no_username(client):
    response = client.post(
        "/users", 
        json={ "email": TEST_USER_EMAIL, "plain_password": TEST_USER_PASSWORD }
    )

    assert response.status_code == 422

def test_post_no_email(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "plain_password": TEST_USER_PASSWORD }
    )

    assert response.status_code == 422

def test_post_no_password(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL }
    )

    assert response.status_code == 422

def test_post_invalid_email(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": "mail", "plain_password": TEST_USER_PASSWORD }
    )

    assert response.status_code == 422

def test_post_short_password(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": "Short1!" }
    )

    assert response.status_code == 422

def test_post_no_uppercase_password(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": "short1!" }
    )

    assert response.status_code == 422

def test_post_no_lowercase_password(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": "SHORT1!" }
    )
    assert response.status_code == 422

def test_post_no_digit_password(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": "short1!" }
    )

    assert response.status_code == 422

def test_post_no_special_char_password(client):
    response = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": "short1!" }
    )

    assert response.status_code == 422


def test_post_duplicate_username(client):
    response1 = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": TEST_USER_PASSWORD }
    )

    assert response1.status_code == 201

    response2 = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": "test2@example.com", "plain_password": "TestPassword2!" }
    )

    assert response2.status_code == 409

def test_post_duplicate_email(client):
    response1 = client.post(
        "/users", 
        json={ "username": TEST_USER_USERNAME, "email": TEST_USER_EMAIL, "plain_password": TEST_USER_PASSWORD }
    )

    assert response1.status_code == 201

    response2 = client.post(
        "/users", 
        json={ "username": "TestUser2", "email": TEST_USER_EMAIL, "plain_password": "TestPassword2!" }
    )

    assert response2.status_code == 409

import re

@pytest.mark.asyncio
async def test_account_activation_from_email(client, db_session, mailpit):
    response = client.post(
        "/users",
        json={
            "username": TEST_USER_USERNAME,
            "email": TEST_USER_EMAIL,
            "plain_password": TEST_USER_PASSWORD,
        },
    )

    assert response.status_code == 201
    assert len(mailpit.messages) == 1

    message = mailpit.messages[0]
    email_body = str(message.body)

    match = re.search(r'/activate\?token=([^"<\s]+)', email_body)
    assert match is not None

    activation_token = match.group(1)

    activation_response = client.patch(
        f"/users/activate/{activation_token}"
    )

    assert activation_response.status_code == 200
    assert activation_response.json()["is_activated"] is True

    result = await db_session.exec(
        select(User).where(User.username == TEST_USER_USERNAME)
    )
    user = result.one()

    assert user.is_activated is True

@pytest.mark.asyncio
async def test_expired_activation_token_is_rejected(client, db_session):
    response = client.post(
        "/users",
        json={
            "username": TEST_USER_USERNAME,
            "email": TEST_USER_EMAIL,
            "plain_password": TEST_USER_PASSWORD,
        },
    )

    assert response.status_code == 201

    result = await db_session.exec(
        select(User).where(User.username == TEST_USER_USERNAME)
    )
    user = result.one()

    expired_token = create_token(
        user_id=user.id,
        username=user.username,
        token_type=TokenTypes.ACTIVATE,
        expires_delta=timedelta(seconds=-1),
    )

    activation_response = client.patch(
        f"/users/activate/{expired_token}"
    )

    assert activation_response.status_code == 400
    assert activation_response.json()["detail"] == "Invalid token"

    await db_session.refresh(user)
    assert user.is_activated is False

@pytest.mark.asyncio
async def test_wrong_token_type_is_rejected(client, db_session):
    response = client.post(
        "/users",
        json={
            "username": TEST_USER_USERNAME,
            "email": TEST_USER_EMAIL,
            "plain_password": TEST_USER_PASSWORD,
        },
    )

    assert response.status_code == 201

    result = await db_session.exec(
        select(User).where(User.username == TEST_USER_USERNAME)
    )
    user = result.one()

    wrong_type_token = create_token(
    user.id,
    user.username,
    TokenTypes.CHANGE_PASSWORD,
    timedelta(minutes=5),
)

    response = client.patch(f"/users/activate/{wrong_type_token}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Wrong token type"