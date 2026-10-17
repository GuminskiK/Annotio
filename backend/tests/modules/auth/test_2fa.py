import pyotp
import pytest
from sqlmodel import func, select

from src.app.modules.auth.models.BackupCodes import BackupCode
from src.app.modules.auth.models.Users import User


@pytest.mark.asyncio
async def test_enable_2fa(logged_in_client, user, db_session):


    setup_response = logged_in_client.post("/2fa/setup")
    assert setup_response.status_code == 200
    setup_data = setup_response.json()
    assert setup_data["secret"]
    assert setup_data["qr_code_uri"].startswith("otpauth://")

    totp_code = pyotp.TOTP(setup_data["secret"]).now()
    enable_response = logged_in_client.post("/2fa/enable", json={"code": totp_code})

    assert enable_response.status_code == 200
    enable_data = enable_response.json()
    assert enable_data["message"] == "2FA successfully enabled"
    assert len(enable_data["backup_codes"]) == 10

    refreshed_user = await db_session.get(User, user.id)
    assert refreshed_user is not None
    assert refreshed_user.is_totp_enabled is True
    assert refreshed_user.totp_secret == setup_data["secret"]

    backup_count = await db_session.exec(
        select(func.count())
        .select_from(BackupCode)
        .where(BackupCode.user_id == user.id)
    )
    assert backup_count.one() == 10

@pytest.mark.asyncio
async def test_enable_2fa_with_invalid_code(logged_in_client, user):

    setup_response = logged_in_client.post("/2fa/setup")
    assert setup_response.status_code == 200
    setup_data = setup_response.json()
    assert setup_data["secret"]
    assert setup_data["qr_code_uri"].startswith("otpauth://")

    invalid_code = "123456"
    enable_response = logged_in_client.post("/2fa/enable", json={"code": invalid_code})

    assert enable_response.status_code == 401
    enable_data = enable_response.json()
    assert enable_data["detail"] == "Invalid 2FA code"

@pytest.mark.asyncio
async def test_enable_2fa_without_setup(logged_in_client, user):

    enable_response = logged_in_client.post("/2fa/enable", json={"code": "123456"})

    assert enable_response.status_code == 400
    enable_data = enable_response.json()
    assert enable_data["detail"] == "2FA setup not initiated"

@pytest.mark.asyncio
async def test_enable_2fa_when_already_enabled(logged_in_client, user, db_session):
    user.is_totp_enabled = True
    await db_session.commit()

    setup_response = logged_in_client.post("/2fa/setup")
    setup_response = setup_response.json()
    assert setup_response["detail"] == "2FA is already enabled"

@pytest.mark.asyncio
async def test_login_with_2fa(client, user, db_session, fake_redis):
    user.is_totp_enabled = True
    user.totp_secret = pyotp.random_base32()
    await db_session.commit()

    totp_code = pyotp.TOTP(user.totp_secret).now()

    login_response = client.post(
        "/auth/login",
        data={
            "username": "TestUser",
            "password": "TestPassword123!",
        },
    )
    assert login_response.status_code == 202
    login_data = login_response.json()
    assert login_data["status"] == "mfa_required"
    assert "mfa_token" in login_data

    mfa_token = login_data["mfa_token"]

    mfa_response = client.post(
        "/auth/login/mfa",
        json={"mfa_token": mfa_token, "mfa_code": totp_code},
    )
    assert mfa_response.status_code == 200
    mfa_data = mfa_response.json()
    assert mfa_data["message"] == "Logged in successfully!"

