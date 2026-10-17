import pytest
import re
from fastapi import BackgroundTasks
from src.app.modules.auth.models.Users import User
from tests.conftest import TEST_USER_USERNAME
from tests.modules.auth.test_user_creation import TEST_USER_EMAIL
from sqlmodel import select
from src.app.modules.auth.utils.auth_utils import verify_password
from src.app.modules.auth.services.users_service import change_password, send_change_password_mail

NEW_PASSWORD = "NewTestPassword123!"

@pytest.mark.asyncio
async def test_change_password(client, user, db_session, mailpit):

    background_tasks = BackgroundTasks()
    await send_change_password_mail(db_session, str(user.email), background_tasks)
    await background_tasks()

    assert len(mailpit.messages) == 1

    message = mailpit.messages[0]
    email_body = str(message.body)

    match = re.search(r'/reset-password\?token=([^"<\s]+)', email_body)
    assert match is not None

    activation_token = match.group(1)

    await change_password(db_session, activation_token, NEW_PASSWORD)

    result = await db_session.exec(
        select(User).where(User.username == TEST_USER_USERNAME)
    )

    user = result.one()

    assert user.hashed_password != NEW_PASSWORD
    assert verify_password(NEW_PASSWORD, user.hashed_password)

@pytest.mark.asyncio
async def test_no_email_for_password_reset(db_session, mailpit):
    background_tasks = BackgroundTasks()
    response = await send_change_password_mail(
        db_session,
        "nonexistent@example.com",
        background_tasks,
    )
    assert response["message"].startswith("If an account")

    assert len(mailpit.messages) == 0


@pytest.mark.asyncio
async def test_invalid_token_for_password_reset(client):
    invalid_token = "invalidtoken"

    activation_response = client.patch(
        f"/users/change_password/{invalid_token}",
        json={"plain_password": NEW_PASSWORD}
    )
    assert activation_response.status_code == 400

@pytest.mark.asyncio
async def test_username_change(authorized_client, user, db_session):
    new_username = "NewTestUser"

    response = authorized_client.patch(
        "/users/me",
        json={"username": new_username}
    )

    assert response.status_code == 200

    result = await db_session.exec(
        select(User).where(User.id == user.id)
    )
    updated_user = result.one()

    assert updated_user.username == new_username

@pytest.mark.asyncio
async def test_password_change(authorized_client, user, db_session):

    response = authorized_client.patch(
        "/users/me",
        json={"plain_password": NEW_PASSWORD}
    )

    assert response.status_code == 200

    result = await db_session.exec(
        select(User).where(User.id == user.id)
    )
    updated_user = result.one()

    assert verify_password(NEW_PASSWORD, updated_user.hashed_password)