import pytest
from sqlmodel import select

from src.app.modules.auth.models.Users import User


@pytest.mark.asyncio
async def test_superuser_can_grant_superuser_status(client, user, override_admin, db_session):
    response = client.patch(
        f"/users/change_role/{user.id}",
        params={"is_superuser": True},
    )

    assert response.status_code == 200
    assert response.json()["is_superuser"] is True

    result = await db_session.exec(select(User).where(User.id == user.id))
    updated_user = result.one()
    assert updated_user.is_superuser is True


@pytest.mark.asyncio
async def test_superuser_can_add_business_role(client, user, override_admin, db_session):
    response = client.patch(
        f"/users/{user.id}/roles",
        json={"role": "auditor"},
    )

    assert response.status_code == 200
    assert response.json()["roles"] == ["worker", "auditor"]

    result = await db_session.exec(select(User).where(User.id == user.id))
    updated_user = result.one()
    assert [getattr(role, "value", role) for role in updated_user.roles] == ["worker", "auditor"]


@pytest.mark.asyncio
async def test_regular_user_cannot_grant_superuser_status(authenticated_client, user):
    response = authenticated_client.patch(
        f"/users/change_role/{user.id}",
        params={"is_superuser": True},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only admin can perform this action"
